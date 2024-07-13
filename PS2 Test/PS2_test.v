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
		
	reg [15:0] addr = 0;
	always @(posedge CLOCK_50)
	begin
		addr <= addr + 1;
	end
	
	altsyncram	altsyncram_component (
				  .address_a (addr),
				  .clock0 (CLOCK_50),
				  .data_a (received_data),
				  .wren_a (received_data_en),
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
				  .rden_a (1'b0)
				  );
defparam
		altsyncram_component.clock_enable_input_a = "BYPASS",
		altsyncram_component.clock_enable_output_a = "BYPASS",
		altsyncram_component.intended_device_family = "Cyclone V",
		altsyncram_component.lpm_hint = "ENABLE_RUNTIME_MOD=YES, INSTANCE_NAME=DATA_MEM",
		altsyncram_component.lpm_type = "altsyncram",
		altsyncram_component.numwords_a = 65536,
		altsyncram_component.operation_mode = "SINGLE_PORT",
		altsyncram_component.outdata_aclr_a = "NONE",
		altsyncram_component.outdata_reg_a = "UNREGISTERED",
		altsyncram_component.power_up_uninitialized = "FALSE",
		altsyncram_component.widthad_a = 16,
		altsyncram_component.width_a = 8,
		altsyncram_component.width_byteena_a = 1;

	
endmodule