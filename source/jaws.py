import os
import sys
import argparse
import collections
import re

import gcnet2nc, promice2nc, aaws2nc
from datetime import datetime

from common import relative_path


def get_parser():
	parser = argparse.ArgumentParser()
	parser.add_argument(
		"input_file", nargs='?',
		help="Raw L2 data file to convert to netCDF (or use -i option)",
		type=str)
	parser.add_argument(
		"output_file", nargs='?',
		help="Output netCDF file (or use -o option)", type=str)
	parser.add_argument(
		"-i", "--fl_in", "--input",
		help=("Raw L2 data file to convert to netCDF "
			  "(or use first positional argument)"),
		type=str)
	parser.add_argument(
		"-o", "--fl_out", "--output",
		help="Output netCDF file (or use last positional argument)",
		type=str)
	parser.add_argument(
		"-3", "--format3", "--3", "--fl_fmt=classic",
		help="Output file in netCDF3 CLASSIC (32-bit offset) storage format",
		action="store_true")
	parser.add_argument(
		"-4", "--format4", "--4", "--netcdf4",
		help="Output file in netCDF4 (HDF5) storage format",
		action="store_true")
	parser.add_argument(
		"-5", "--format5", "--5", "--fl_fmt=64bit_data",
		help=("Output file in netCDF3 64-bit data"
			  " (i.e., CDF5, PnetCDF) storage format"),
		action="store_true")
	parser.add_argument(
		"-6", "--format6", "--6", "--64",
		"--fl_fmt=64bit_offset",
		help="Output file in netCDF3 64-bit offset storage format",
		action="store_true")
	parser.add_argument(
		"-7", "--format7", "--7", "--fl_fmt=netcdf4_classic",
		help="Output file in netCDF4 CLASSIC format (3+4=7)",
		action="store_true")
	parser.add_argument(
		"-d", "--derive_times",
		help=("For GCNet, extra variables ('month', 'day' and 'hour')"
			  " will be derived for further analysis. It will take more time"),
		action="store_true")
	parser.add_argument(
		"-s", "--station_name",
		help="Override default station name",
		type=str)
	parser.add_argument(
		"-t", "--timezone",
		help="Change the timezone, default is UTC",
		default='UTC', type=str)
	parser.add_argument(
		"-f", "--fillvalue_float",
		help="Override default float _FillValue", type=float)
	parser.add_argument(
		"-D", "--dbg_lvl", "--debuglevel",
		help="Debug-level is lvl", default=0, type=int)
	
	'''
	
	/* Argument --debuglevel in increasing levels of verbosity */
	jaws_dbg_quiet, /* 0 */ Quiet all non-error messages
	jaws_dbg_std,   /* 1 */ Elapsed time
	jaws_dbg_fl,	/* 2 */ Input/Output Filepaths
	jaws_dbg_coords,/* 3 */ lat, lon, stn_name
	jaws_dbg_time,  /* 4 */ time and sza
	jaws_dbg_var1,  /* 5 */ For GCNet- quality control variables, For PROMICE- lat_GPS, lon_GPS
	jaws_dbg_var2,  /* 6 */ For GCNet- month and day, For PROMICE- ice_velocity
	
	'''
	return parser


def parse_args(args):
	return get_parser().parse_args(args)


def get_stations():
	"""Read stations.txt and parse it into an ordered dict."""
	with open(relative_path('resources/stations.txt')) as stream:
		stations = stream.read().split('\n')

	# remove blank lines
	stations = [i.strip() for i in stations if i.strip()]
	ordered = collections.OrderedDict(blank=[])

	errmsg = 'stations.txt is corrupted or malformed and could not be parsed.'
	for station in stations:
		match = re.match('(.+) +(-?[0-9.]+) + (-?[0-9.]+) *(.*)$', station)
		if not match:
			raise RuntimeError(errmsg)
		name, lon, lat, name2 = match.groups()
		lon, lat = float(lon), float(lat)
		name2 = name2.strip()
		value = [lon, lat, name2] if name2 else [lon, lat]
		ordered[name.strip()] = value

	return ordered

def get_input_file(args):
	"""
	Retrieve the input file.

	If no input file is specified, show error message and exit.
	"""
	if args.input_file:
		return args.input_file
	if args.fl_in:
		return args.fl_in
	print('Error: You failed to provide input file!\n')
	get_parser().print_help()
	print('\n')
	print(
		'Post questions, suggestions, patches at https://github.com/jaws/jaws')
	sys.exit(1)


def get_output_file(args, input_file, stations):
	"""
	Retrieve the output file.

	If the file isn't specified explicitly via command line arguments,
	construct the output file based on the input file.
	"""
	if args.output_file:
		return args.output_file
	if args.fl_out:
		return args.fl_out

	basename = os.path.basename(input_file).split('.')[0]
	try:
		name_number = int(basename[:2])
	except ValueError:
		return basename + '.nc'

	stations = list(stations.keys())
	if 0 < name_number < 24:
		basename = stations[name_number]
	elif basename[2:] == 'c':
		basename = stations[name_number - 6]
	else:
		pass

	return basename + '.nc'


def dispatch_converter(args, input_file, output_file, stations):
	"""
	Call the converter corresponding to the given format.

	Reads the first character of the input file, and uses it to guess the
	format of the input file and dispatch the right converter.
	"""
	with open(input_file) as stream:
		char = stream.readline()[0]

	converters = {
		'D': gcnet2nc.gcnet2nc,
		'Y': promice2nc.promice2nc,
		'#': aaws2nc.aaws2nc}

	errmsg = 'Conversion failed: unsupported input file format.'
	if char in converters:
		converters[char](args, input_file, output_file, stations)
	else:
		raise RuntimeError(errmsg)

def main(args):
	start_time = datetime.now()

	stations = get_stations()
	input_file = get_input_file(args)
	output_file = get_output_file(args, input_file, stations)

	dispatch_converter(args, input_file, output_file, stations)

	if args.dbg_lvl > 0:
		print('Elapsed time: {}'.format(datetime.now() - start_time))

	if args.dbg_lvl > 1:
		msg = 'Converted {} to {}'.format(
			os.path.basename(input_file), output_file)
		print(msg)


if __name__ == '__main__':
	main(parse_args(sys.argv[1:]))
