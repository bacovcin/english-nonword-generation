# english-nonword-generation
A python script using CMUdict and Subtlex data to create lists of pseudowords for English lexical decision experiments

# How to use

This script must be run from the command line and requires Python3 to be installed.
The basic use is: python generate-nonwords.py

You can also set flags to change the behaviour of the script. Flag descriptions have the following format: NAME (syntax) description
	NUMSYL (numsyl=X) Sets the number of syllables in the generated items to X with a default of 1
	NUMWORDS (numwords=X) Sets the number of words generated to X with a default of 10
	NOSTRESS (nostress) Does not require stress on first syllable. By default primary stress will always be on the first syllable
	NOBREAKS (nobreaks) Does not mark syllable breaks with a -. By default syllable breaks are marked with a -
	FILE (file=X) Gives the name of the output file. By default the output will be printed to stdout

# Sources 
CMUdict uses a submodule taken from: https://github.com/cmusphinx/cmudict
SUBTLEX frequency data acquired from: http://www.ugent.be/pp/experimentele-psychologie/en/research/documents/subtlexus
