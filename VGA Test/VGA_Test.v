module VGA_Test(CLOCK_50,VGA_R, VGA_G, VGA_B, VGA_CLK, VGA_SYNC_N, VGA_BLANK_N, VGA_HS, VGA_VS);

input				CLOCK_50;
output [7:0]	VGA_R;
output [7:0]	VGA_B;
output [7:0]	VGA_G;
output			VGA_CLK;
output			VGA_SYNC_N;
output			VGA_BLANK_N;
output			VGA_HS;
output			VGA_VS;



/*********************
 **      CLOCK      **
 *********************/
reg vga_clk = 1'b0;
always @(posedge CLOCK_50)
begin
	vga_clk = ~vga_clk;
end



/*********************
 **     COUNTER     **
 *********************/
reg [9:0] hCount = 0;
reg [9:0] vCount = 0;

reg [20:0] rCount = 0;
reg signed [20:0] radius = -2500;

always @(posedge vga_clk)
begin
	hCount <= hCount == 799 ? 0 : hCount + 1;
	if (hCount == 799) vCount <= vCount == 524 ? 0 : vCount + 1;
	
	if (hDisp && vDisp)
	begin
		rCount <= rCount == 3072000 ? 0 : rCount + 1;
		if (rCount == 3072000) radius <= radius + 1;
	end
end



/*********************
 **      INPUT      **
 *********************/
wire [3:0] memData;

altsyncram	altsyncram_component (
				  .address_a (((hCount+1)%800) + ((vCount+1)%525) * 640),
				  .clock0 (CLOCK_50),
				  .data_a (),
				  .wren_a (1'b0),
				  .q_a (memData),
				  .aclr0 (1'b0),
				  .aclr1 (1'b0),
				  .addressstall_a (1'b0),
				  .byteena_a (1'b1),
				  .clocken0 (1'b1),
				  .clocken1 (1'b1),
				  .clocken2 (1'b1),
				  .clocken3 (1'b1),
				  .rden_a ((hDisp && vDisp) || hCount == 799 && vCount == 524),
				  );
defparam
		altsyncram_component.clock_enable_input_a = "BYPASS",
		altsyncram_component.clock_enable_output_a = "BYPASS",
		altsyncram_component.init_file = "mem_init.mif",
		altsyncram_component.intended_device_family = "Cyclone V",
		altsyncram_component.lpm_hint = "ENABLE_RUNTIME_MOD=YES, INSTANCE_NAME=DATA_MEM",
		altsyncram_component.lpm_type = "altsyncram",
		altsyncram_component.numwords_a = 307200,
		altsyncram_component.operation_mode = "SINGLE_PORT",
		altsyncram_component.outdata_aclr_a = "NONE",
		altsyncram_component.outdata_reg_a = "UNREGISTERED",
		altsyncram_component.power_up_uninitialized = "FALSE",
		altsyncram_component.widthad_a = 19,
		altsyncram_component.width_a = 4,
		altsyncram_component.width_byteena_a = 1;



/*********************
 **     PALETTE     **
 *********************/
reg [23:0] palette[0:15];

initial
begin
	palette[0] = 24'h090300;
	palette[1] = 24'hDB2D20;
	palette[2] = 24'h01A252;
	palette[3] = 24'hFDED02;
	palette[4] = 24'h01A0E4;
	palette[5] = 24'hA16A94;
	palette[6] = 24'hB5E4F4;
	palette[7] = 24'hA5A2A2;
	palette[8] = 24'h5C5855;
	palette[9] = 24'hE8BBD0;
	palette[10] = 24'h3A3432;
	palette[11] = 24'h4A4543;
	palette[12] = 24'h807D7C;
	palette[13] = 24'hD6D5D4;
	palette[14] = 24'hCDAB53;
	palette[15] = 24'hF7F7F7;
end
									 

									 
									 
/*********************
 **   ASSIGNMENTS   **
 *********************/
wire hDisp = hCount < 640;
wire vDisp = vCount < 480;

wire p = (hCount-320) * (hCount-320) + (vCount-240)*(vCount-240) <= radius*radius ? 9 : memData;
assign VGA_CLK = vga_clk;
assign VGA_HS = ~(656 <= hCount && hCount < 752);
assign VGA_VS = ~(490 <= vCount && vCount < 492);
assign VGA_R = palette[p][23:16];
assign VGA_G = palette[p][15:8];
assign VGA_B = palette[p][7:0];
assign VGA_BLANK_N = ~(~hDisp || ~vDisp);
assign VGA_SYNC_N = 1'b1;


endmodule