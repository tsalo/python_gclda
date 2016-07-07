from gclda.gclda_dataset import gclda_dataset
from gclda.gclda_model 	 import gclda_model
import cPickle as pickle
import os
import gzip

# ----------------------------------------------------
# --- Set up Dataset Label & Load/Save Directories ---
# ----------------------------------------------------

# Set up dataset-label and dataset-directory we use for building dataset object
datasetLabel = '2015Filtered2'
dataDirectory = '../Data/Datasets/'

# Root-directory where model results are saved
results_rootdir = 'gclda_results'

# -----------------------------------------
# --- Configure the sampling parameters ---
# -----------------------------------------

current_iter  	 	= 0 	# Current model iteration: if 0, start new model, otherwise load & resume sampling existing model
total_iterations 	= 1000 	# Total iterations to run from current point
save_freq 		 	= 10 	# How often we save a model object and topic-distributions to file
loglikely_Freq 	 	= 5 	# How often we compute log-likelihood (which slows sampling down but is useful for tracking model progress)
sampler_verbosity 	= 2 	# How much information about sampler gets printed to console (2 is max, 0 is min)

# ------------------------------------------
# --- Configure gcLDA model Parameters   ---
# ------------------------------------------

nt  		= 100	# Number of topics
nr 			= 2 	# Number of subregions (should work with any number)
alpha 		= .1 	# Prior count on topics for each doc
beta 		= .01 	# Prior count on word-types for each topic
gamma 		= .01 	# Prior count added to y-counts when sampling z assignments
delta 		= 1.0 	# Prior count on subregions for each topic
roi 		= 50 	# Default ROI (default covariance spatial region we regularize towards)
dobs 		= 25 	# Sample constant (# observations weighting sigma in direction of default covariance)
symmetric 	= True	# Use symmetry constraint on subregions? (symmetry requires nr = 2)

seed_init 	= 1 	# Initial value of random seed

# --- Set up model_str identifier for saving/loading results based on model params ---
model_str = '%s_%dT_%dR_alpha%.3f_beta%.3f_gamma%.3f_delta%.3f_%ddobs_%.1froi_%dsymmetric_%d' % (datasetLabel,
	nt, nr, alpha, beta, gamma, delta, dobs, roi, symmetric, seed_init)

# -----------------------------------------------------------------------------
# --- Set up directories and either Initialize model or load existing model ---
# -----------------------------------------------------------------------------

# --- Set up directories for saving/loading results ---
if not os.path.isdir(results_rootdir):
	os.mkdir(results_rootdir)
results_outputdir = '%s/%s' % (results_rootdir, model_str)
if not os.path.isdir(results_outputdir):
	os.mkdir(results_outputdir)

# --- Initialize / Load model object (depending on current_iter) ---
if current_iter == 0:
	# --- If starting a new model ---
	# Create dataset object & Import data
	dat = gclda_dataset(datasetLabel,dataDirectory)
	dat.importAllData()
	dat.displayDatasetSummary()
	# Initialize the model using the dataset object and all parameter settings
	model = gclda_model(dat, nt, nr , alpha, beta, gamma, delta, dobs, roi, symmetric, seed_init)
	model.initialize()
else:
	# --- If resuming existing model ---
	print "Resuming model at iteration %02d" % current_iter
	# Set up loadfilename
	results_loadfile = "%s/results_iter%02d.p" % (results_outputdir, current_iter) 	
	# Load compressed model object
	with gzip.open(results_loadfile,'rb') as f:
		model = pickle.load(f)

# Display initialized model summary
model.displayModelSummary()

# ----------------------------------------------------------------
# --- Run the gclda model until model.iter = total_iterations  ---
# ----------------------------------------------------------------

for i in range(model.iter, total_iterations):
	# Cycle through an iteration of all parameter updates (update_z, update_y, update_regions)
	model.runCompleteIteration(loglikely_Freq, sampler_verbosity) 
	
	# Save model and topic-word distributions every 'savefreq' iterations
	if ((model.iter % save_freq )==0):
		# Set up savefilenames
		savefilenm_pickle 	= "%s/results_iter%02d.p" % (results_outputdir, model.iter) 
		savefilenm_csv 		= "%s/results_iter%02d.csv" % (results_outputdir, model.iter) 
		
		# Save a gzip compressed model object to file
		with gzip.open(savefilenm_pickle,'wb') as f:
			pickle.dump(model,f)
		
		# Print topic-word distributions
		model.printTopicWordProbs(savefilenm_csv) 

