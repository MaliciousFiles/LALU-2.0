module PS2_test(CLOCK_50, PS2_CLK, PS2_DATA, KEY0);
	input				CLOCK_50;
	inout  			PS2_CLK;
	inout  			PS2_DATA;
	input 			KEY0;
		
	
	wire [7:0] received_data;
	wire received_data_en;
	
	wire reset = ~KEY0;
	
	
	PS2_Controller #(.INITIALIZE_MOUSE(0)) inst (
		.CLOCK_50(CLOCK_50),
		.reset(reset),
		.PS2_CLK(PS2_CLK),
		.PS2_DAT(PS2_DATA),
		.received_data(received_data),
		.received_data_en(received_data_en),
	);
		
	
	reg [9:0] addr = 0;
	always @(posedge CLOCK_50 or posedge reset)
	begin	
		if (reset) addr <= 0;
		else if (received_data_en) addr <= addr + 1;
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
		altsyncram_component.numwords_a = 1024,
		altsyncram_component.operation_mode = "SINGLE_PORT",
		altsyncram_component.outdata_aclr_a = "NONE",
		altsyncram_component.outdata_reg_a = "UNREGISTERED",
		altsyncram_component.power_up_uninitialized = "FALSE",
		altsyncram_component.widthad_a = 10,
		altsyncram_component.width_a = 8,
		altsyncram_component.width_byteena_a = 1;
	
endmodule