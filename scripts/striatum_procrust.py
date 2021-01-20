import matplotlib.pyplot as plt
import numpy as np
import scipy.io as sio
import pandas as pd
import mapalign.align as align
import os

#df = pd.read_table('participants.tsv')
#subjects = df.participant_id.to_list() 
#subjects = [ s.strip('sub-') for s in subjects ]

grad_dir = snakemake.input.grads_path
subjects = snakemake.params.subj

out_path = snakemake.params.aligned_grads_path

def make_out_dir(out_path):

	#Make subdirectories to save files
	filename = out_path
	if not os.path.exists(os.path.dirname(filename)):
	    try:
	        os.makedirs(os.path.dirname(filename))
	    except OSError as exc: # Guard against race condition
	        if exc.errno != errno.EEXIST:
	          raise
	          
def get_array_sized_fixed(Data_array, maximum_rows):

	array_length = np.shape(Data_array)[0]

	mismatch_count = maximum_rows - array_length

	if mismatch_count != 0:
	
		for i in range(mismatch_count):

			row = np.random.randint(1,array_length-1)  #Ignoring the first and last to eliminate averaging error for n-1 + n+1 /2
			new_row = (Data_array[row-1,:] + Data_array[row+1,:])/2
			Data_array = np.insert(Data_array,row,new_row,0)

	return Data_array	          

make_out_dir(out_path)

embeddings_R = []
embeddings_L = []

for i in subjects:
    emb_R = np.load(grad_dir+'/sub-%s_R_emb.npy' % i)
    emb_R = get_array_sized_fixed(emb_R, 1885)
    embeddings_R.append(emb_R)
    emb_L = np.load(grad_dir+'/sub-%s_L_emb.npy' % i)
    emb_L = get_array_sized_fixed(emb_L, 1885)
    embeddings_L.append(emb_L)


realigned_R, xfms_R = align.iterative_alignment(embeddings_R, n_iters=5)
native_R = np.array(embeddings_R)
realigned_R = np.array(realigned_R)
xfms_R = np.array(xfms_R)

realigned_L, xfms_L = align.iterative_alignment(embeddings_L, n_iters=5)
native_L = np.array(embeddings_L)
realigned_L = np.array(realigned_L)
xfms_L = np.array(xfms_L)



#print(e3b_realigned[0,:,0])

for i,sub in enumerate(subjects):

	R_gradient = realigned_R[i,:,:]
	L_gradient = realigned_L[i,:,:]

	grad_df = pd.DataFrame({'R_grad_1': R_gradient[:,0], 'R_grad_2': R_gradient[:,1],
			'R_grad_3': R_gradient[:,2], 'R_grad_4': R_gradient[:,3], 'L_grad_1': L_gradient[:,0],
			 'L_grad_2': L_gradient[:,1], 'L_grad_3': L_gradient[:,2], 'L_grad_4': L_gradient[:,3]})

	grad_df.to_csv(out_path+'/sub-'+sub+'_gradients.csv', index=False)






