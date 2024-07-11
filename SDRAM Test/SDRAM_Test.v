module SDRAM_Test(CLOCK_50, DRAM_DQ, DRAM_ADDR, DRAM_BA, DRAM_CLK, DRAM_CKE, DRAM_LDQM, DRAM_UDQM, DRAM_WE_N, DRAM_CAS_N, DRAM_RAS_N, DRAM_CS_N,
						LEDR0,LEDR1,LEDR2,LEDR3, LEDR5, HEX0, HEX1, HEX2, HEX3, HEX4, HEX5);

input CLOCK_50;
inout [15:0] DRAM_DQ;
output [12:0] DRAM_ADDR;
output [1:0] DRAM_BA;
output DRAM_CLK;
output DRAM_CKE;
output DRAM_LDQM;
output DRAM_UDQM;
output DRAM_WE_N;
output DRAM_CAS_N;
output DRAM_RAS_N;
output DRAM_CS_N;
output LEDR0;
output LEDR1;
output LEDR2;
output LEDR3;
output LEDR5;
output [6:0] HEX0;
output [6:0] HEX1;
output [6:0] HEX2;
output [6:0] HEX3;
output [6:0] HEX4;
output [6:0] HEX5;

wire dram_clk;
pll_100m pll (.inclk0(CLOCK_50), .c0(dram_clk));

reg [24:0] wr_addr;
reg [15:0] wr_data;
reg 	     wr_en;

reg [24:0] rd_addr;
wire [15:0] rd_data;
wire			rd_ready;
wire			busy;
reg 	     rd_en;

reg reset = 0;

reg [3:0] ready = 4'hF;
reg [15:0] data = 0;

reg [20:0] counter = 100000;
always @(posedge dram_clk)
begin
if (counter > 0)
begin
	
	counter <= counter - 1;
	
	reset <= ~(counter > 99990);
	
	if (counter == 99000)
	begin
		wr_addr <= 25'h0;//25'h2A3;
		wr_data <= 16'h3D1A;
		wr_en <= 1;
	end
	if (wr_en && busy)
	begin
		wr_addr <= 0;
		wr_data <= 0;
		wr_en <= 0;
	end
	
	if (~wr_en && counter == 50000)
	begin
		rd_addr <= 25'h0;//25'h2A3;
		rd_en <= 1;
	end
	if (rd_en && busy)
	begin
		rd_addr <= 0;
		rd_en <= 0;
	end
	
	if (rd_data == 16'h3D1A)
	begin
		data <= rd_data;
	end
	
	if (rd_ready)
	begin
		ready <= 49999-counter;
	end
end
end

sdram_controller inst (
	.wr_addr(wr_addr),
	.wr_data(wr_data),
	.wr_enable(wr_en),
	.rd_addr(rd_addr),
	.rd_data(rd_data),
	.rd_enable(rd_en),
	.rd_ready(rd_ready),
	.busy(busy),
	.rst_n(reset),
	.clk(dram_clk),
	
	.addr(DRAM_ADDR),
	.bank_addr(DRAM_BA),
	.data(DRAM_DQ),
	.clock_enable(DRAM_CKE),
	.cs_n(DRAM_CS_N),
	.cas_n(DRAM_CAS_N),
	.we_n(DRAM_WE_N),
	.data_mask_low(DRAM_LDQM),
	.data_mask_high(DRAM_UDQM)
);

assign DRAM_CLK = dram_clk;
assign LEDR0 = ready[0];
assign LEDR1 = ready[1];
assign LEDR2 = ready[2];
assign LEDR3 = ready[3];

hex H3 (.in(data[15:12]), .out(HEX3));
hex H2 (.in(data[11:8]), .out(HEX2));
hex H1 (.in(data[7:4]), .out(HEX1));
hex H0 (.in(data[3:0]), .out(HEX0));

assign LEDR5 = counter == 0;


endmodule