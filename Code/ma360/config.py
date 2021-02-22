config = dict(
	random_seed = 100,
	available_bw_number = 86,
	available_user_number = 48, #zhd-delete
	available_video_number = 9,
	sample_ratio_col = 181,
	sample_ratio_row = 91,
	total_tile_number = 32,
	# 4M - 20M
	video_size = [0.004, 0.012, 0.02, 0.04, 0.06],  #100 300 500 1000 1500    x / 25000
	video_quality = [0.6896, 0.817, 0.876, 0.9392, 0.943],
	# x = np.array([34.48, 38.39, 40.85, 42.35, 43.80, 45.55, 46.51, 46.96, 47.30, 47.65, 47.68])
	# y = np.array([100,   200,   300,   400,   500,   700,   800,   1000,  1200,  1500,  2000])
	video_size_level = 5, 
	state_info = 4,  #viewpoint, bandwidth, rate, remaining
	state_len = 6,
	bw_lr_ref_number = 3,
	vp_lr_ref_number = 3,
	delay_param = 0.01, #reward_delay
	cost_param = 1, #reward_cost
	diff_param = 0,
	cost_param_greedy = 1, #greedy params
	start_up_delay = 5,
	nearest_k = 5,
	bw_max = 25000,
	bw_min = 4000,
	bw_max_min = 21000,
	train_bw_number = 86,
	train_vp_number = 8,
	test_vp_index = 8,
	predict_bandwidth_len = 10,
	#-----------------------need to change------------------
	model_info = '_k_5_768_512_318_'
	#-----------------------need to change------------------

	)

mfac_model = dict(\
	value_coef=0.1, 
	ent_coef=0.08, 
	gamma=0.95, 
	batch_size=64, 
	learning_rate=1e-4,
	#-----------------------need to change------------------
	seed = 666,
	hidden_size = [768, 512]
	#-----------------------need to change------------------
	)
	
runner = dict(
	tau = 0.01,
	print_every=100
	)
	
viewpoint_model = dict(
    batch_size=64,
    max_seq_len=20,
    num_blocks=32,
    block_classes=2,
    lstm_hidden_size=32,
    learning_rate=0.001,
    multi_step_initial_step=5,
    multi_step_test_step=3,
    # lstm_vp_path = 'prediction/tmp/lstm_viewpoint/rnn_1562134420.492755_model.ckpt-4801',
    lstm_vp_path = 'prediction/tmp/lstm_viewpoint/rnn_1563848782.982903_model.ckpt-4801' #new

)

viewpoint_model_train = dict(
    batch_size=64,
    max_seq_len=20,
    num_blocks=32,
    block_classes=2,
    lstm_hidden_size=32,
    learning_rate=0.001,
    multi_step_initial_step=5,
    multi_step_test_step=3,
)


bandwidth_model = dict(
    batch_size=64,
    max_seq_len=20,
    lstm_hidden_size=8,
    learning_rate=0.001,
    multi_step_initial_step=5,
    multi_step_test_step=10,
    lstm_bw_path = 'prediction/tmp/lstm_bandwidth/rnn_1564007517.7074728_model.ckpt-5801'
)

bandwidth_model_train = dict(
    batch_size=64,
    max_seq_len=20,
    lstm_hidden_size=8,
    learning_rate=0.001,
    multi_step_initial_step=5,
    multi_step_test_step=10,
)


viewpoint_train = dict(
    train_step=5000,
    train_save_step=200,
    test_step_per_epoch=50,
    logging_step=20,
)

bandwidth_train = dict(
    train_step=6000,
    train_save_step=200,
    test_step_per_epoch=50,
    logging_step=20,
)
