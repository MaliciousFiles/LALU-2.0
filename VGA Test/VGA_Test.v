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
	vga_clk <= ~vga_clk;
end



/*********************
 **     H FRAME     **
 *********************/
// 0 = hsync
// 1 = back porch
// 2 = display
// 3 = front porch
reg [2:0] hStage = 3'b0;

reg [7:0] hs_count = 8'd190;
reg [6:0] hbp_count = 7'd95;
reg [10:0] hdisp_count = 11'd1270;
reg [5:0] hfp_count = 6'd30;

always @(posedge CLOCK_50)
begin
	if (hStage == 0)
	begin
		if (hs_count == 1)
		begin
			hStage <= hStage+3'b1;
			hs_count <= 8'd190;
		end
		else hs_count <= hs_count - 8'b1;
	end
	
	else if (hStage == 1)
	begin
		if (hbp_count == 1)
		begin
			hStage <= hStage+3'b1;
			hbp_count <= 7'd95;
		end
		else hbp_count <= hbp_count - 7'b1;
	end
	
	else if (hStage == 2)
	begin
		if (hdisp_count == 1)
		begin
			hStage <= hStage+3'b1;
			hdisp_count <= 11'd1270;
		end
		else hdisp_count <= hdisp_count - 11'b1;
	end
	
	else if (hStage == 3)
	begin
		if (hfp_count == 1)
		begin
			hStage <= 3'b0;
			hfp_count <= 6'd30;
		end
		else hfp_count <= hfp_count - 6'b1;
	end
end



/*********************
 **     V FRAME     **
 *********************/
// 0 = vsync
// 1 = back porch
// 2 = display
// 3 = front porch
reg [2:0] vStage = 0;


reg [1:0] vs_count = 2'd3;
reg [5:0] vbp_count = 6'd33;
reg [8:0] vdisp_count = 9'd480;
reg [3:0] vfp_count = 4'd10;

always @(negedge hStage[1])
begin
	if (vStage == 0)
	begin
		if (vs_count == 1)
		begin
			vStage <= vStage+3'b1;
			vs_count <= 2'd2;
		end
		else vs_count <= vs_count - 2'b1;
	end
	
   else if (vStage == 1)
	begin
		if (vbp_count == 1)
		begin
			vStage <= vStage+3'b1;
			vbp_count <= 6'd33;
		end
		else vbp_count <= vbp_count - 6'b1;
	end
	
	else if (vStage == 2)
	begin
		if (vdisp_count == 1)
		begin
			vStage <= vStage+3'b1;
			vdisp_count <= 9'd480;
		end
		else vdisp_count <= vdisp_count - 9'b1;
	end
	
	else if (vStage == 3)
	begin
		if (vfp_count == 1)
		begin
			vStage <= 3'b0;
			vfp_count <= 4'd10;
		end
		else vfp_count <= vfp_count - 4'b1;
	end
end



/*********************
 **      INPUT      **
 *********************/
wire [7:0] memData;
reg [2:0] addr = 3'b0;

reg [7:0] red;
reg [7:0] green;
reg [7:0] blue;

always @(posedge CLOCK_50)
begin
	if (addr == 0) red <= memData;
	if (addr == 1) green <= memData;
	if (addr == 2) blue <= memData;
	
	adr <= addr == 2 ? 1'b0 : addr + 3'b1;
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
assign VGA_CLK = vga_clk;
assign VGA_HS = ~(hStage == 0);
assign VGA_VS = ~(vStage == 0);
assign VGA_R = red;
assign VGA_G = green;
assign VGA_B = blue;
assign VGA_BLANK_N = ~(vStage == 1 || vStage == 3 || hStage == 1 || hStage == 3);
assign VGA_SYNC_N = 1'b1;



endmodule