python scripts/test_voxcpm_ft_infer.py \
    --ckpt_dir checkpoints/0.5B/step_0002000 \
    --text "Cho em xin ít phút để trao đổi về hợp đồng Thẻ tín dụng của mình nha anh" \
    --output ft_test.wav

python scripts/test_voxcpm_ft_infer.py \
    --ckpt_dir checkpoints/0.5B/step_0002000 \
    --text "Cho em xin ít phút để trao đổi về hợp đồng Thẻ tín dụng của mình nha anh" \
    --output ft_test.wav \
    --prompt_audio examples/audio.wav \
    --prompt_text "Trong bầu không khí náo nhiệt của rạp hát, hùng thủ rút khẩu súng Derringer 44 ly, dí sát đầu tổng thống mà nã đạn."