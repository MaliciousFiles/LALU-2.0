module PS2_test(CLOCK_50, PS2_CLK, PS2_DATA, HEX0, HEX1, HEX2, HEX3, HEX4, HEX5, LEDR0, KEY0, TEST);
	input			CLOCK_50;
	input				KEY0;
	output	[6:0]	HEX0;
	output	[6:0]	HEX1;
	output	[6:0]	HEX2;
	output	[6:0]	HEX3;
	output	[6:0]	HEX4;
	output	[6:0]	HEX5;
	output			LEDR0;
	inout  			PS2_CLK;
	inout  			PS2_DATA;
	input	 			TEST;
	
	//wire [31:0] readdata;
	
	wire command_was_sent;
	wire error_communication_timed_out;
	wire [7:0] received_data;
	wire received_data_en;
	
	PS2_Controller inst (
		.CLOCK_50(CLOCK_50),
		.reset(KEY0),
		.PS2_CLK(PS2_CLK),
		.PS2_DAT(PS2_DATA),
		.received_data(received_data),
		.received_data_en(received_data_en)
	);
	
	wire [3:0] test;
	assign test = {1'b0, command_was_sent, error_communication_timed_out, received_data_en};
	
	hex H5(.in(received_data[7:4]), .out(HEX5));
	hex H4(.in(received_data[3:0]), .out(HEX4));
	hex H0(.in(test), .out(HEX0));
	
	assign LEDR0 = received_data[0];
	
	//PS2 inst (
	//	.clk_clk(CLOCK_50),
	//	.ps2_0_external_interface_CLK(PS2_CLK),
	//	.ps2_0_external_interface_DAT(PS2_DATA),
	//	.reset_reset_n(KEY0),
	//	.readdata(readdata)
	//);
	
	//wire [15:0] data;
	//assign data = PS2_DATA;
	
	//hex H5(.in(readdata[31:28]), .out(HEX5));
	//hex H4(.in(readdata[27:24]), .out(HEX4));
	//hex H3(.in(readdata[23:20]), .out(HEX3));
	//hex H2(.in(readdata[19:16]), .out(HEX2));
	//hex H1(.in(readdata[15:12]), .out(HEX1));
	//hex H0(.in(readdata[11:8]), .out(HEX0));
	
	//assign LEDR0 = TEST;
	
endmodule