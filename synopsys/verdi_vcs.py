#!/usr/bin/env python3

import argparse
import subprocess
import sys
import os
from typing import List, Optional
from pathlib import Path

class ICSimulation:
    def __init__(self):
        self.vcs_options = {
            'timescale': '1ns/1ps',
            'debug_flags': ['-debug_all', '-debug_acc', '-debug_pp', '-debug_region'],
            'coverage_options': ['-cm line+cond+fsm+branch+tgl'],
            'compiler_flags': ['-full64', '-sverilog', '-v2k_generate'],
            'assertions': ['-assert', '-assert svaext'],
            'directories': ['rtl/', 'tb/', 'include/']
        }
        
        self.verdi_options = {
            'debug_modes': ['syn', 'rtl', 'gate'],
            'databases': ['.fsdb', '.vcd', '.vpd'],
            'nWave_options': ['-ssf', '-fsdb'],
            'analysis_options': ['upf', 'power']
        }

    def run_vcs(self, args: argparse.Namespace) -> None:
        """
        Execute VCS compilation and simulation with specified options
        """
        try:
            # Build compilation command
            compile_cmd = ['vcs']
            compile_cmd.extend(['-timescale=' + args.timescale])
            
            if args.debug:
                compile_cmd.extend(['-debug_all'])
            if args.coverage:
                compile_cmd.extend(self.vcs_options['coverage_options'])
            if args.full64:
                compile_cmd.extend(['-full64'])
            if args.sverilog:
                compile_cmd.extend(['-sverilog'])
            
            # Add source files
            if args.filelist:
                compile_cmd.extend(['-f', args.filelist])
            for file in args.sources:
                compile_cmd.append(file)
                
            # Add include directories
            if args.includes:
                for inc in args.includes:
                    compile_cmd.extend(['+incdir+' + inc])
            
            print(f"Executing VCS compilation: {' '.join(compile_cmd)}")
            subprocess.run(compile_cmd, check=True)
            
            # Run simulation if requested
            if args.run:
                sim_cmd = ['./simv']
                if args.gui:
                    sim_cmd.append('-gui')
                if args.plusargs:
                    sim_cmd.extend(args.plusargs)
                
                print(f"Executing simulation: {' '.join(sim_cmd)}")
                subprocess.run(sim_cmd, check=True)
                
        except subprocess.CalledProcessError as e:
            print(f"Error in VCS execution: {e}", file=sys.stderr)
            sys.exit(1)

    def run_verdi(self, args: argparse.Namespace) -> None:
        """
        Execute Verdi debug session with specified options
        """
        try:
            cmd = ['verdi']
            
            if args.mode:
                cmd.extend(['-mode', args.mode])
            if args.ssf:
                cmd.extend(['-ssf', args.ssf])
            if args.upf:
                cmd.extend(['-upf', args.upf])
            
            # Add source files
            if args.filelist:
                cmd.extend(['-f', args.filelist])
            for file in args.sources:
                cmd.append(file)
            
            print(f"Launching Verdi: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"Error launching Verdi: {e}", file=sys.stderr)
            sys.exit(1)

    def setup_parser(self) -> argparse.ArgumentParser:
        """
        Set up command line argument parser for IC simulation tools
        """
        parser = argparse.ArgumentParser(
            description='Run VCS simulation and Verdi debug for IC design',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest='tool', help='Choose tool to run')
        
        # VCS subparser
        vcs_parser = subparsers.add_parser('vcs', help='Run VCS compilation and simulation')
        vcs_parser.add_argument('-timescale', default=self.vcs_options['timescale'],
                               help='Simulation timescale')
        vcs_parser.add_argument('-debug', action='store_true',
                               help='Enable debug mode')
        vcs_parser.add_argument('-coverage', action='store_true',
                               help='Enable coverage collection')
        vcs_parser.add_argument('-full64', action='store_true',
                               help='Use 64-bit compilation')
        vcs_parser.add_argument('-sverilog', action='store_true',
                               help='Enable SystemVerilog features')
        vcs_parser.add_argument('-f', '--filelist', help='File containing source files list')
        vcs_parser.add_argument('-run', action='store_true',
                               help='Run simulation after compilation')
        vcs_parser.add_argument('-gui', action='store_true',
                               help='Run simulation in GUI mode')
        vcs_parser.add_argument('-includes', nargs='+', help='Include directories')
        vcs_parser.add_argument('sources', nargs='*', help='Source files')
        vcs_parser.add_argument('-plusargs', nargs='*',
                               help='Runtime plusargs for simulation')
        
        # Verdi subparser
        verdi_parser = subparsers.add_parser('verdi', help='Launch Verdi debug session')
        verdi_parser.add_argument('-mode', choices=self.verdi_options['debug_modes'],
                                help='Debug mode')
        verdi_parser.add_argument('-ssf', help='Signal dump file')
        verdi_parser.add_argument('-upf', help='UPF file for power analysis')
        verdi_parser.add_argument('-f', '--filelist', help='File containing source files list')
        verdi_parser.add_argument('sources', nargs='*', help='Source files')
        
        return parser

    def main(self, args: Optional[List[str]] = None) -> None:
        """
        Main entry point for the script
        """
        parser = self.setup_parser()
        args = parser.parse_args(args)
        
        if args.tool is None:
            parser.print_help()
            sys.exit(1)
            
        if args.tool == 'vcs':
            self.run_vcs(args)
        elif args.tool == 'verdi':
            self.run_verdi(args)

if __name__ == '__main__':
    tool = ICSimulation()
    tool.main()
