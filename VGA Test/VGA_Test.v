module VGA_Test(CLOCK_50,VGA_R, VGA_G, VGA_B, VGA_CLK, VGA_SYNC_N, VGA_BLANK_N, VGA_HS, VGA_VS, ohs, ovs);

input				CLOCK_50;
output [7:0]	VGA_R;
output [7:0]	VGA_B;
output [7:0]	VGA_G;
output			VGA_CLK;
output			VGA_SYNC_N;
output			VGA_BLANK_N;
output			VGA_HS;
output			VGA_VS;
output [2:0]	ohs;
output [2:0]	ovs;



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
		hs_count <= hs_count - 8'b1;
		
		if (hs_count == 0)
		begin
			hStage <= hStage+3'b1;
			hs_count <= 8'd190;
		end
	end
	
	else if (hStage == 1)
	begin
		hbp_count <= hbp_count - 7'b1;
		
		if (hbp_count == 0)
		begin
			hStage <= hStage+3'b1;
			hbp_count <= 7'd95;
		end
	end
	
	else if (hStage == 2)
	begin
		hdisp_count <= hdisp_count - 11'b1;
		
		if (hdisp_count == 0)
		begin
			hStage <= hStage+3'b1;
			hdisp_count <= 11'd1270;
		end
	end
	
	else if (hStage == 3)
	begin
		hfp_count <= hfp_count - 6'b1;
		
		if (hfp_count == 0)
		begin
			hStage <= 3'b0;
			hfp_count <= 6'd30;
		end
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


reg [1:0] vs_count = 2'd2;
reg [5:0] vbp_count = 6'd33;
reg [8:0] vdisp_count = 9'd480;
reg [3:0] vfp_count = 4'd10;

always @(negedge hStage[1])
begin
	if (vStage == 0)
	begin
		vs_count <= vs_count - 2'b1;
		
		if (vs_count == 0)
		begin
			vStage <= vStage+3'b1;
			vs_count <= 2'd2;
		end
	end
	
	else if (vStage == 1)
	begin
		vbp_count <= vbp_count - 6'b1;
		
		if (vbp_count == 0)
		begin
			vStage <= vStage+3'b1;
			vbp_count <= 6'd33;
		end
	end
	
	else if (vStage == 2)
	begin
		vdisp_count <= vdisp_count - 9'b1;
		
		if (vdisp_count == 0)
		begin
			vStage <= vStage+3'b1;
			vdisp_count <= 9'd480;
		end
	end
	
	else if (vStage == 3)
	begin
		vfp_count <= vfp_count - 4'b1;
		
		if (vfp_count == 0)
		begin
			vStage <= 3'b0;
			vfp_count <= 4'd10;
		end
	end
end



/*********************
 **   ASSIGNMENTS   **
 *********************/
assign VGA_CLK = vga_clk;
assign VGA_HS = hStage != 0;
assign VGA_VS = vStage != 0;
assign VGA_R = vStage == 2 && hStage == 2 ? 8'h3D : 8'b0;
assign VGA_G = vStage == 2 && hStage == 2 ? 8'hD1 : 8'b0;
assign VGA_B = vStage == 2 && hStage == 2 ? 8'h98 : 8'b0;
assign VGA_BLANK_N = vStage == 1 || vStage == 3 || hStage == 1 || hStage == 3;
assign VGA_SYNC_N = 1'b0;
assign ohs = hStage;
assign ovs = vStage;


endmodule