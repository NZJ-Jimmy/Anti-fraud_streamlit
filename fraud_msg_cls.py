# %%
classes = ['冒充公检法及政府机关类', '冒充军警购物类诈骗', '冒充电商物流客服类', '冒充领导、熟人类', '无风险',
       '网络婚恋、交友类', '网黑案件', '虚假信用服务类', '虚假网络投资理财类', '虚假购物、服务类']
# test_text = "您好，抖音上发现有人提供替考驾驶证服务，每科仅需1400元，微信号为wei1in12345，如有需要请联系，我们保证快速通过考试。"

import torch
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# %%
from sklearn.preprocessing import LabelEncoder
from transformers import BertTokenizer, BertForSequenceClassification
import torch

lb = LabelEncoder()
lb.classes_ = classes
# Use Huawei Nezha model
tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')

def encode_texts(texts):
    return tokenizer(
        texts,
        padding='max_length',
        truncation=True,
        max_length=128,
        return_tensors='pt',
    )

# Use Huawei Nezha model
model = BertForSequenceClassification.from_pretrained('bert-base-chinese', num_labels=len(classes)).to(device)
model.load_state_dict(torch.load(r"model/final_model.pth"))
if torch.cuda.is_available():
    model = model.cuda()

# %%
def predict(test_text):
    output = model(**encode_texts([test_text]).to(device))
    output = output.logits
    output = torch.softmax(output, dim=1)
    output = output.cpu().detach().numpy()
    output = output[0]
    output = list(zip(lb.classes_, output))
    output = sorted(output, key=lambda x: x[1], reverse=True)
    return output

# %%
if __name__ == "__main__":
    test_text = "【顺丰】尊敬的客户，您使用顺丰的频率较高，现赠送您暖风扇一台，请添加支付宝好友进行登记领取。"
    print(predict(test_text))
