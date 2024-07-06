module PS2_test(CLOCK_50, PS2_CLK, PS2_DATA, HEX0, HEX1, HEX2, HEX3, KEY0);
	input			CLOCK_50;
	input				KEY0;
	output	[6:0]	HEX0;
	output	[6:0]	HEX1;
	output	[6:0]	HEX2;
	output	[6:0]	HEX3;
	inout 			PS2_CLK;
	inout				PS2_DATA;
	
	PS2 inst (
		.clk_clk(CLOCK_50),
		.ps2_0_external_interface_CLK(PS2_CLK),
		.ps2_0_external_interface_DAT(PS2_DATA),
		.reset_reset_n(KEY0)
	);
	
	wire [15:0] data;
	assign data = PS2_DATA;
	
	hex H0(.in(data[15:12]), .out(HEX0));
	hex H1(.in(data[11:8]), .out(HEX1));
	hex H2(.in(data[7:4]), .out(HEX2));
	hex H3(.in(data[3:0]), .out(HEX3));
	
endmodule