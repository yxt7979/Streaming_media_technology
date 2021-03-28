package modules.clients;

simple client{
    parameters:
    	@display("i=abstract/people;is=l");
    double lambda = default(1);//泊松分布的一个参数
	double W = default(1); //TODO
	double check_time = default(0.1);//检测下载状况的时间间隔
	double RTT = default(0.1);//估计的往返时延
    gates:
    	inout client_port;
}


