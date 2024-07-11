module SDRAM_Test(CLOCK_50, DRAM_DQ, DRAM_ADDR, DRAM_BA, DRAM_CLK, DRAM_CKE, DRAM_LDQM, DRAM_UDQM, DRAM_WE_N, DRAM_CAS_N, DRAM_RAS_N, DRAM_CS_N,
						LEDR0,LEDR1,LEDR2,LEDR3);

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

reg [12:0] addr = 0;
reg [15:0] data = 0;

reg [3:0] delay = 4'hF;
reg [6:0] count = 100;
always @(posedge CLOCK_50)
begin
	count <= count - 1;
	
	if (count == 100)
	begin
		data <= 16'hA3FB;
		addr <= 13'd52;
	end
	if (count == 99)
	begin
		addr <= 13'b0;
	end
	
	if (count == 60)
	begin
		addr <= 13'd52;
	end
	
	if (count < 60 && DRAM_DQ == 16'hA3FB)
	begin
		delay <= 59-count;
	end
	
	if (count == 0 && delay == 4'hF) delay <= 4'hA;
end

assign LEDR0 = delay[0];
assign LEDR1 = delay[1];
assign LEDR2 = delay[2];
assign LEDR3 = delay[3];

assign DRAM_ADDR = addr;
assign DRAM_BA = 2'b0;
assign DRAM_DQ = data;

assign DRAM_CLK = CLOCK_50;
assign DRAM_CKE = 1'b1;
assign DRAM_LDQM = 1'b0;
assign DRAM_UDQM = 1'b0;
assign DRAM_WE_N = 1'b1;
assign DRAM_RAS_N = 1'b0;
assign DRAM_CAS_N = 1'b0;
assign DRAM_CS_N = 1'b0;


endmodule