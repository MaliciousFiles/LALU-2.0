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

always @(posedge vga_clk)
begin
	hCount <= hCount == 799 ? 0 : hCount + 1;
	if (hCount == 799) vCount <= vCount == 524 ? 0 : vCount + 1;
end



/*********************
 **      INPUT      **
 *********************/
wire [7:0] memData;
reg [2:0] addr = 3'b0;

reg [7:0] red = 8'b1;
reg [7:0] green = 8'b1;
reg [7:0] blue = 8'b1;

always @(posedge CLOCK_50)
begin
	if (addr == 1) red <= memData;
	if (addr == 2) green <= memData;
	if (addr == 0) blue <= memData;
	
	addr <= addr == 2 ? 3'b0 : addr + 3'b1;
end

altsyncram	altsyncram_component (
				  .address_a (addr),
				  .clock0 (CLOCK_50),
				  .data_a (),
				  .wren_a (1'b0),
				  .q_a (memData),
				  .aclr0 (1'b0),
				  .aclr1 (1'b0),
				  .address_b (),
				  .addressstall_a (1'b0),
				  .addressstall_b (1'b0),
				  .byteena_a (1'b1),
				  .byteena_b (1'b1),
				  .clock1 (),
				  .clocken0 (1'b1),
				  .clocken1 (1'b1),
				  .clocken2 (1'b1),
				  .clocken3 (1'b1),
				  .data_b (),
				  .eccstatus (),
				  .q_b (),
				  .rden_a (1'b1),
				  .rden_b (1'b1),
				  .wren_b ()
				  );
defparam
		altsyncram_component.clock_enable_input_a = "BYPASS",
		altsyncram_component.clock_enable_output_a = "BYPASS",
		altsyncram_component.init_file = "RAMCONTENTS_RAM_2.mif",
		altsyncram_component.intended_device_family = "Cyclone V",
		altsyncram_component.lpm_hint = "ENABLE_RUNTIME_MOD=YES, INSTANCE_NAME=DATA_MEM",
		altsyncram_component.lpm_type = "altsyncram",
		altsyncram_component.numwords_a = 3,
		altsyncram_component.operation_mode = "SINGLE_PORT",
		altsyncram_component.outdata_aclr_a = "NONE",
		altsyncram_component.outdata_reg_a = "UNREGISTERED",
		altsyncram_component.power_up_uninitialized = "FALSE",
		altsyncram_component.widthad_a = 3,
		altsyncram_component.width_a = 8,
		altsyncram_component.width_byteena_a = 1;



/*********************
 **   ASSIGNMENTS   **
 *********************/
wire hDisp = hCount < 640;
wire vDisp = vCount < 480;


assign VGA_CLK = vga_clk;
assign VGA_HS = ~(656 <= hCount && hCount < 752);
assign VGA_VS = ~(490 <= vCount && vCount < 492);
assign VGA_R = (hCount-320) * (hCount-320) + (vCount-240)*(vCount-240) <= 10000 ? 8'hFF : red;
assign VGA_G = (hCount-320) * (hCount-320) + (vCount-240)*(vCount-240) <= 10000 ? 8'h00 : green;
assign VGA_B = (hCount-320) * (hCount-320) + (vCount-240)*(vCount-240) <= 10000 ? 8'h00 : blue;
assign VGA_BLANK_N = ~(~hDisp || ~vDisp);
assign VGA_SYNC_N = 1'b1;


endmodule