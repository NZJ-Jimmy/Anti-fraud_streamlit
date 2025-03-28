import fraud_msg_cls
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device is: {device}")

test_text = "【顺丰】尊敬的客户，您使用顺丰的频率较高，现赠送您暖风扇一台，请添加支付宝好友进行登记领取。"

print(fraud_msg_cls.predict(test_text))

ans = fraud_msg_cls.predict(test_text)

res, max_prob = max(ans, key=lambda x: x[1])
print(f"预测的诈骗类型为: {res}")
