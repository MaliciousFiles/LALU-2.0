module PS2_test(CLOCK_50, PS2_CLK, PS2_DAT, KEY0, KEY1, KEY2, KEY3, HEX0, HEX1, HEX2, HEX3, HEX4, HEX5, LEDR0, LEDR1, LEDR2, LEDR3);
   /*******************************************************************************
   ** The inputs are defined here                                                **
   *******************************************************************************/
   input KEY0;
	input KEY1;
	input KEY2;
   input KEY3;
	input CLOCK_50;

   /*******************************************************************************
   ** The outputs are defined here                                               **
   *******************************************************************************/
   output [6:0] HEX0;
	output [6:0] HEX1;
	output [6:0] HEX2;
	output [6:0] HEX3;
	output [6:0] HEX4;
	output [6:0] HEX5;
	output reg LEDR0 = 0;
	output reg LEDR1 = 0;
	output reg LEDR2 = 0;
	output reg LEDR3 = 0;
	

   /*******************************************************************************
   ** The inouts are defined here                                                **
   *******************************************************************************/
   inout PS2_CLK;
   inout PS2_DAT;

	wire poll_print = ~KEY0;

	wire poll_raw = ~KEY1;

	wire rd_clk = ~KEY2;

	wire reset = ~KEY3;

		wire wr_clk = CLOCK_50;

	hex H0 (.in(data_print[3:0]), .out(HEX0));
	hex H1 (.in(data_print[7:4]), .out(HEX1));
	hex H2 (.in(data_raw[3:0]), .out(HEX2));
	hex H3 (.in(data_raw[7:4]), .out(HEX3));
	hex H4 (.in(data_raw[11:8]), .out(HEX4));
	hex H5 (.in(data_raw[15:12]), .out(HEX5));
	
	reg [7:0]  data_print;
   reg [15:0] data_raw;

	
   /*******************************************************************************
   ** The module functionality is described here                                 **
   *******************************************************************************/
   wire [7:0] ps2_data;
	wire available;

   PS2_Controller inst (
       .CLOCK_50(wr_clk),
       .reset(reset),
       .received_data(ps2_data),
       .received_data_en(available),
       .PS2_CLK(PS2_CLK),
       .PS2_DAT(PS2_DAT)
   );



    /*********************
     *      PARSING      *
     *********************/
    reg [102:0] depressed = 0;
    reg [7:0] ascii_val = 8'hFF;
    reg [7:0] raw_val = 8'hFF;

    wire Lshft = depressed[8'h28];
    wire Lctrl = depressed[8'h29];
    wire Lalt = depressed[8'h2A];
    wire Lwin = depressed[8'h2B];
    wire Rshft = depressed[8'h2C];
    wire Rctrl = depressed[8'h2D];
    wire Ralt = depressed[8'h2E];
    wire Rwin = depressed[8'h2F];
    wire caps = depressed[8'h27];

    reg [2:0] pause_key = 0;

    reg break_code = 0;
    reg ex_code = 0;
    always @(posedge wr_clk) begin
		  if (available) LEDR3 <= 1;
		  
        break_code <= ps2_data == 8'hF0;
        if (ps2_data != 8'hF0) ex_code <= ps2_data == 8'hE0;

        if (!available || break_code) begin
            ascii_val <= 8'hFF;
            raw_val <= 8'hFF;
        end

        if (available && pause_key == 0) begin
				LEDR2 <= 1;
            if (!ex_code && ps2_data == 8'h76) begin
                if (!break_code) begin
                    ascii_val <= 8'hFF;
                    raw_val <= 8'h00;
						  LEDR0 <= 1;
                end
					 else LEDR1 <= 1;

                depressed[8'h00] <= !break_code;
            end

            if (!ex_code && ps2_data == 8'h15) begin
                if (!break_code) begin
                    ascii_val <= Lctrl || Lalt || Lwin || Rctrl || Ralt || Rwin ? 8'hFF : Lshft || Rshft || caps ? "Q" : "q";
                    raw_val <= 8'h41;
                end

                depressed[8'h41] <= !break_code;
            end

            if (ex_code && ps2_data == 8'h74) begin
                if (!break_code) begin
                    ascii_val <= 8'hFF;
                    raw_val <= 8'h66;
                end

                depressed[8'h66] <= !break_code;
            end
        end
        else begin
            pause_key <= pause_key - 1;
        end
    end


   wire [7:0] printable_data;
   Keyboard_Buffer #(.WIDTH(8)) printable_buf (
        .wr_clk(wr_clk),
        .wr_data(ascii_val),
        .we(ascii_val != 8'hFF),

        .poll(poll_print),
        .reset(reset),
        .rd_clk(rd_clk),
        .rd_data(printable_data)
    );

   wire [15:0] raw_data;
   Keyboard_Buffer #(.WIDTH(16)) raw_buf (
        .wr_clk(wr_clk),
        .wr_data({Lctrl, Lshft, Lalt, Lwin, Rctrl, Rshft, Ralt, Rwin, caps, raw_val}),
        .we(raw_val != 8'hFF),

        .poll(poll_raw),
        .reset(reset),
        .rd_clk(rd_clk),
        .rd_data(raw_data)
    );

	 always @(posedge wr_clk) begin
		data_print <= printable_data;
		data_raw <= raw_data;
	 end
endmodule