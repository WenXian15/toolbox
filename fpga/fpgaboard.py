import csv
import os

class fpga_board:
  def __init__(self, model):
    self.model = model

  def generate_vivado_io(csv_data, connector_mappings):
  """
    Generate Vivado TCL constraints file from CSV data mapping I/O names to Prodigy connectors.
    
    Args:
        csv_data (str): CSV string with format "io_name,prodigy_connector,pins_no,io_voltage"
        connector_mappings (dict): Dictionary mapping connector pins to FPGA pins
        
    Returns:
        str: Vivado TCL constraints file content
  """

    # Parse the csv code
    io_mappings = []
    csv_reader = csv.reader(io.StringIO(csv_data))
    for row in csv_reader:
      if len(row) >= 4:
        io_name, prodigy_connector, pin_no, io_voltage = row[:4]
        io_mappings.append({
            'io_name': io_name,
            'prodigy_connector': prodigy_connector,
            'pin_no': pin_no,
            'io_voltage': io_voltage
        })

    # Generate the TCL constraints
    tcl_content = []
    tcl_content.append("# Automatically generated Vivado constraints file")
    tcl_content.append("# Generated from I/O mapping CSV data\n")
    
    for mapping in io_mappings:
        io_name = mapping['io_name']
        connector = mapping['prodigy_connector']
        pin_no = mapping['pin_no']
        io_voltage = mapping['io_voltage']
        
        # Look up the FPGA pin from the connector mappings
    if connector in connector_mappings and pin_no in connector_mappings[connector]:
        fpga_pin_info = connector_mappings[connector][pin_no]
        fpga_pin = fpga_pin_info[0]  # First element is the FPGA pin number
        bank = fpga_pin_info[1]      # Second element is the bank number
        pin_desc = fpga_pin_info[2]  # Third element is the pin description
            
        # Generate the TCL constraint line
        tcl_content.append(f"# {io_name} - {connector}.{pin_no} - {pin_desc} ({bank})")
        tcl_content.append(f"set_property PACKAGE_PIN {fpga_pin} [get_ports {io_name}]")
        tcl_content.append(f"set_property IOSTANDARD LVCMOS{io_voltage.replace('V', '')} [get_ports {io_name}]")
            
        # Add a blank line for readability
        tcl_content.append("")
    else:
        tcl_content.append(f"# ERROR: Could not find mapping for {io_name} on {connector}.{pin_no}")
        tcl_content.append("")
    
    return "\n".join(tcl_content)
