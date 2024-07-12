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

reg [5:0] charX = 0;
reg [4:0] charY = 0;
reg [3:0] charU = 0;
reg [4:0] charV = 0;

always @(posedge vga_clk)
begin
	// NEW LINE
	if (hCount == 799)
	begin
		hCount <= 0;
		charX <= 0;
		charU <= 0;
		
		// NEW FRAME
		if (vCount == 524)
		begin
			vCount <= 0;
			charY <= 0;
			charV <= 0;
		end
		// MID FRAME
		else
		begin
			vCount <= vCount + 1;
			
			// END CHAR
			if (charV == 19)
			begin
				charV <= 0;
				charY <= charY + 1;
			end
			// MID CHAR
			else
			begin
				charV <= charV + 1;
			end
		end
	end
	// MID LINE
	else
	begin
		hCount <= hCount + 1;
		
		// END CHAR
		if (charU == 9)
		begin
			charU <= 0;
			charX <= charX + 1;
		end
		// MID CHAR
		else
		begin
			charU <= charU + 1;
		end
	end
end



/*********************
 **      INPUT      **
 *********************/
wire [7:0] memData;
wire [10:0] addr = charX + charY * 64;

altsyncram	altsyncram_component (
				  .address_a (/*addr*/10'b0),
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
				  .eccstatus (),
				  .rden_a (/*vDisp && hDisp*/1'b1)
				  );
defparam
		altsyncram_component.clock_enable_input_a = "BYPASS",
		altsyncram_component.clock_enable_output_a = "BYPASS",
		//altsyncram_component.init_file = "mem_init.mif",
		altsyncram_component.intended_device_family = "Cyclone V",
		altsyncram_component.lpm_hint = "ENABLE_RUNTIME_MOD=YES, INSTANCE_NAME=DATA_MEM",
		altsyncram_component.lpm_type = "altsyncram",
		altsyncram_component.numwords_a = 1536,
		altsyncram_component.operation_mode = "SINGLE_PORT",
		altsyncram_component.outdata_aclr_a = "NONE",
		altsyncram_component.outdata_reg_a = "UNREGISTERED",
		altsyncram_component.power_up_uninitialized = "FALSE",
		altsyncram_component.widthad_a = 11,
		altsyncram_component.width_a = 8,
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
 **      CHARS      **
 *********************/
reg [0:199] characters[0:26];

initial
begin
	characters[0]  = 200'b0;
	characters[1] = 200'b00001100000001001000000100100000010010000001001000001000010000100001000011111100001000010001000000100100000010010000001001000000100100000010010000001001000000100000000000000000000000000000000000000000;
	characters[2] = 200'b01111110000100000100010000001001000000100100000010010000001001000001000111111000010000010001000000100100000010010000001001000000100100000010010000010001111110000000000000000000000000000000000000000000;
	characters[3] = 200'b00011111100010000000010000000001000000000100000000010000000001000000000100000000010000000001000000000100000000010000000001000000000100000000001000000000011111100000000000000000000000000000000000000000;
	characters[4] = 200'b01111110000100000100010000001001000000100100000010010000001001000000100100000010010000001001000000100100000010010000001001000000100100000010010000010001111110000000000000000000000000000000000000000000;
	characters[5] = 200'b00111111100100000000010000000001000000000100000000010000000001000000000111111110010000000001000000000100000000010000000001000000000100000000010000000000111111100000000000000000000000000000000000000000;
	characters[6] = 200'b00111111100100000000010000000001000000000100000000010000000001111111100100000000010000000001000000000100000000010000000001000000000100000000010000000001000000000000000000000000000000000000000000000000;
	characters[7] = 200'b00011111100010000000010000000001000000000100000000010000000001000000000100000000010000111001000000100100000010010000001001000000100100000010001000001000011111100000000000000000000000000000000000000000;
	characters[8] = 200'b01000000100100000010010000001001000000100100000010010000001001000000100111111110010000001001000000100100000010010000001001000000100100000010010000001001000000100000000000000000000000000000000000000000;
	characters[9] = 200'b01111111100000110000000011000000001100000000110000000011000000001100000000110000000011000000001100000000110000000011000000001100000000110000000011000001111111100000000000000000000000000000000000000000;
	characters[10] = 200'b00011111100000000010000000001000000000100000000010000000001000000000100000000010000000001000000000100000000010000000001000000000100100000010010000010000111110000000000000000000000000000000000000000000;
	characters[11] = 200'b01000000100100000010010000001001000001000100001000010000100001001100000111000000010010000001001100000100001000010000100001000001000100000010010000001001000000100000000000000000000000000000000000000000;
	characters[12] = 200'b01000000000100000000010000000001000000000100000000010000000001000000000100000000010000000001000000000100000000010000000001000000000100000000010000000001111111100000000000000000000000000000000000000000;
	characters[13] = 200'b01100001100101001010010100101001001100100100110010010000001001000000100100000010010000001001000000100100000010010000001001000000100100000010010000001001000000100000000000000000000000000000000000000000;
	characters[14] = 200'b01100000100101000010010100001001010000100100100010010010001001001000100100010010010001001001000100100100010010010000101001000010100100001010010000101001000001100000000000000000000000000000000000000000;
	characters[15] = 200'b00111111000100000010010000001001000000100100000010010000001001000000100100000010010000001001000000100100000010010000001001000000100100000010010000001000111111000000000000000000000000000000000000000000;
	characters[16] = 200'b01111110000100000100010000001001000000100100000010010000001001000001000111111000010000000001000000000100000000010000000001000000000100000000010000000001000000000000000000000000000000000000000000000000;
	characters[17] = 200'b00011110000010000100010000001001000000100100000010010000001001000000100100000010010000001001000000100100000010010010001001000100100100001010001000010000011110100000000000000000000000000000000000000000;
	characters[18] = 200'b01111110000100000100010000001001000000100100000010010000001001000001000111111000011000000001011000000100010000010000100001000001000100000100010000001001000000100000000000000000000000000000000000000000;
	characters[19] = 200'b00011110000010000100010000001001000000100100000000010000000000100000000001111000000000010000000000100000000010000000001001000000100100000010001000010000011110000000000000000000000000000000000000000000;
	characters[20] = 200'b01111111100000110000000011000000001100000000110000000011000000001100000000110000000011000000001100000000110000000011000000001100000000110000000011000000001100000000000000000000000000000000000000000000;
	characters[21] = 200'b01000000100100000010010000001001000000100100000010010000001001000000100100000010010000001001000000100100000010010000001001000000100100000010001000010000011110000000000000000000000000000000000000000000;
	characters[22] = 200'b01000000100100000010010000001001000000100100000010010000001000100001000010000100001000010000100001000010000100000100100000010010000001001000000100100000001100000000000000000000000000000000000000000000;
	characters[23] = 200'b01000000100100000010010000001001000000100100000010010000001001000000100100000010010000001001000000100100110010010011001001010010100101001010010100101001100001100000000000000000000000000000000000000000;
	characters[24] = 200'b01000000100100000010001000010000100001000001001000000100100000010010000000110000000011000000010010000001001000000100100000100001000010000100010000001001000000100000000000000000000000000000000000000000;
	characters[25] = 200'b01000000100100000010001000010000100001000001001000000100100000010010000000110000000011000000001100000000110000000011000000001100000000110000000011000000001100000000000000000000000000000000000000000000;
	characters[26] = 200'b01111111100000000010000000010000000010000000001000000001000000000100000000100000000010000000010000000001000000001000000000100000000100000000010000000001111111100000000000000000000000000000000000000000;
end



/*********************
 **   ASSIGNMENTS   **
 *********************/
wire hDisp = hCount < 640;
wire vDisp = vCount < 480;

wire fg = characters[memData[0]][charU + charV * 10];
wire [3:0] p = fg ? 15 : 1;

assign VGA_CLK = vga_clk;
assign VGA_HS = ~(656 <= hCount && hCount < 752);
assign VGA_VS = ~(490 <= vCount && vCount < 492);
assign VGA_R = palette[p][23:16];
assign VGA_G = palette[p][15:8];
assign VGA_B = palette[p][7:0];
assign VGA_BLANK_N = ~(~hDisp || ~vDisp);
assign VGA_SYNC_N = 1'b1;


endmodule