	component PS2 is
		port (
			clk_clk                      : in    std_logic := 'X'; -- clk
			reset_reset_n                : in    std_logic := 'X'; -- reset_n
			ps2_0_external_interface_CLK : inout std_logic := 'X'; -- CLK
			ps2_0_external_interface_DAT : inout std_logic := 'X'  -- DAT
		);
	end component PS2;

	u0 : component PS2
		port map (
			clk_clk                      => CONNECTED_TO_clk_clk,                      --                      clk.clk
			reset_reset_n                => CONNECTED_TO_reset_reset_n,                --                    reset.reset_n
			ps2_0_external_interface_CLK => CONNECTED_TO_ps2_0_external_interface_CLK, -- ps2_0_external_interface.CLK
			ps2_0_external_interface_DAT => CONNECTED_TO_ps2_0_external_interface_DAT  --                         .DAT
		);

