package modules.content;

simple content_distribution {
    parameters:
	double file_size = default (10);//文件大小：一个文件所含块的数量
    int objects = default (100);//目录大小：系统中所含文件的数量
	double alpha = default (1);//流行度分布参数
	double q = default(0);//流行度分布参数
	double cut_off = default(1);//zipf截断点对应的内容标号
	

	@display("i=block/browser;is=l");
	
}
