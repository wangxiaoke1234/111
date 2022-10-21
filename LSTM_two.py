import math
import torch
import torch.nn as nn
import torch.optim as optim
import give_valid_test

# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
device = torch.device("cpu")


def make_batch(train_path, word2number_dict, batch_size, n_step):
    all_input_batch = []
    all_target_batch = []

    text = open(train_path, 'r', encoding='utf-8')  # open the file

    input_batch = []
    target_batch = []
    for sen in text:
        word = sen.strip().split(" ")  # space tokenizer

        if len(word) <= n_step:  # pad the sentence
            word = ["<pad>"] * (n_step + 1 - len(word)) + word

        for word_index in range(len(word) - n_step):
            input = [word2number_dict[n] for n in word[word_index:word_index + n_step]]  # create (1~n-1) as input
            target = word2number_dict[
                word[word_index + n_step]]  # create (n) as target, We usually call this 'casual language model'
            input_batch.append(input)
            target_batch.append(target)

            if len(input_batch) == batch_size:
                all_input_batch.append(input_batch)
                all_target_batch.append(target_batch)
                input_batch = []
                target_batch = []

    return all_input_batch, all_target_batch


def make_dict(train_path):
    text = open(train_path, 'r', encoding='utf-8')  # open the train file
    word_list = set()  # a set for making dict

    for line in text:
        line = line.strip().split(" ")
        word_list = word_list.union(set(line))

    word_list = list(sorted(word_list))  # set to list

    word2number_dict = {w: i + 2 for i, w in enumerate(word_list)}
    number2word_dict = {i + 2: w for i, w in enumerate(word_list)}

    # add the <pad> and <unk_word>
    word2number_dict["<pad>"] = 0
    number2word_dict[0] = "<pad>"
    word2number_dict["<unk_word>"] = 1
    number2word_dict[1] = "<unk_word>"

    return word2number_dict, number2word_dict


class TextRNN(nn.Module):
    def __init__(self):
        super(TextRNN, self).__init__()
        self.C = nn.Embedding(n_class, embedding_dim=emb_size)

        '''define the parameter of RNN'''
        '''begin'''
        ##Complete this code
        self.W1 = nn.Linear(emb_size, n_hidden, bias=False)  # 输入数据参数权重
        self.W2 = nn.Linear(n_hidden, n_hidden, bias=False)
        self.W_xi = nn.Linear(emb_size, n_hidden, bias=False)  # 输入门参数权重
        self.W_hi = nn.Linear(n_hidden, n_hidden, bias=False)
        self.W_xf = nn.Linear(emb_size, n_hidden, bias=False)  # 遗忘门参数权重
        self.W_hf = nn.Linear(n_hidden, n_hidden, bias=False)
        self.W_xo = nn.Linear(emb_size, n_hidden, bias=False)  # 输出门参数权重
        self.W_ho = nn.Linear(n_hidden, n_hidden, bias=False)

        self.W1_y = nn.Linear(n_hidden, n_hidden, bias=False)  # 输入数据参数权重
        self.W2_y = nn.Linear(n_hidden, n_hidden, bias=False)
        self.W_xi_y = nn.Linear(n_hidden, n_hidden, bias=False)  # 输入门参数权重
        self.W_hi_y = nn.Linear(n_hidden, n_hidden, bias=False)
        self.W_xf_y = nn.Linear(n_hidden, n_hidden, bias=False)  # 遗忘门参数权重
        self.W_hf_y = nn.Linear(n_hidden, n_hidden, bias=False)
        self.W_xo_y = nn.Linear(n_hidden, n_hidden, bias=False)  # 输出门参数权重
        self.W_ho_y = nn.Linear(n_hidden, n_hidden, bias=False)

        self.b1 = nn.Parameter(torch.ones([n_hidden]))
        self.b_i = nn.Parameter(torch.ones([n_hidden]))
        self.b_f = nn.Parameter(torch.ones([n_hidden]))
        self.b_o = nn.Parameter(torch.ones([n_hidden]))

        self.b1_y = nn.Parameter(torch.ones([n_hidden]))
        self.b_i_y = nn.Parameter(torch.ones([n_hidden]))
        self.b_f_y = nn.Parameter(torch.ones([n_hidden]))
        self.b_o_y = nn.Parameter(torch.ones([n_hidden]))
        '''end'''

        self.tanh = nn.Tanh()

        self.W3 = nn.Linear(n_hidden, n_class, bias=False)
        self.b2 = nn.Parameter(torch.ones([n_class]))

    def forward(self, X):
        X = self.C(X)
        X = X.transpose(0, 1)  # X : [n_step, batch_size, n_class]
        sample_size = X.size()[1]  #
        '''do this RNN forward'''
        '''begin'''
        ## Complete your code with the hint: a^(t) = tanh(W_{ax}x^(t)+W_{aa}a^(t-1)+b_{a})  y^(t)=softmx(Wa^(t)+b)
        c_t = torch.randn(sample_size, n_hidden)
        c_t_y = torch.randn(sample_size, n_hidden)
        h_t = torch.randn(sample_size, n_hidden)
        h_t_y = torch.randn(sample_size, n_hidden)
        y_outputs = []

        for x in X:
            i = self.tanh(self.W1(x) + self.W2(h_t) + self.b1)  # 输入
            i_t = torch.sigmoid(self.W_xi(x) + self.W_hi(h_t) + self.b_i)  # 输入门控
            f_t = torch.sigmoid(self.W_xf(x) + self.W_hf(h_t) + self.b_f)  # 遗忘门控
            o_t = torch.sigmoid(self.W_xo(x) + self.W_ho(h_t) + self.b_o)  # 输出门控
            c_t = c_t * f_t + i*i_t  # 记忆细胞
            h_t = self.tanh(c_t)*o_t
            y_outputs.append(h_t)

        for y in y_outputs:
            i = self.tanh(self.W1_y(y) + self.W2_y(h_t_y) + self.b1_y)  # 输入
            i_t = torch.sigmoid(self.W_xi_y(y) + self.W_hi_y(h_t_y) + self.b_i_y)  # 输入门控
            f_t = torch.sigmoid(self.W_xf_y(y) + self.W_hf_y(h_t_y) + self.b_f_y)  # 遗忘门控
            o_t = torch.sigmoid(self.W_xo_y(y) + self.W_ho_y(h_t_y) + self.b_o_y)  # 输出门控
            c_t_y = c_t_y * f_t + i * i_t  # 记忆细胞
            h_t_y = self.tanh(c_t_y) * o_t


        model_output = self.W3(h_t_y) + self.b2
        '''end'''

        return model_output


def train_rnnlm():
    model = TextRNN()
    model.to(device)
    print(model)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=learn_rate)

    # Training
    batch_number = len(all_input_batch)
    for epoch in range(all_epoch):
        count_batch = 0
        for input_batch, target_batch in zip(all_input_batch, all_target_batch):
            optimizer.zero_grad()

            # input_batch : [batch_size, n_step, n_class]
            output = model(input_batch)

            # output : [batch_size, n_class], target_batch : [batch_size] (LongTensor, not one-hot)
            loss = criterion(output, target_batch)
            ppl = math.exp(loss.item())
            if (count_batch + 1) % 50 == 0:
                print('Epoch:', '%04d' % (epoch + 1), 'Batch:', '%02d' % (count_batch + 1), f'/{batch_number}',
                      'loss =', '{:.6f}'.format(loss), 'ppl =', '{:.6}'.format(ppl))

            loss.backward()
            optimizer.step()

            count_batch += 1

        # valid after training one epoch
        all_valid_batch, all_valid_target = give_valid_test.give_valid(word2number_dict, n_step)
        all_valid_batch.to(device)
        all_valid_target.to(device)

        total_valid = len(all_valid_target) * 128
        with torch.no_grad():
            total_loss = 0
            count_loss = 0
            for valid_batch, valid_target in zip(all_valid_batch, all_valid_target):
                valid_output = model(valid_batch)
                valid_loss = criterion(valid_output, valid_target)
                total_loss += valid_loss.item()
                count_loss += 1

            print(f'Valid {total_valid} samples after epoch:', '%04d' % (epoch + 1), 'lost =',
                  '{:.6f}'.format(total_loss / count_loss),
                  'ppl =', '{:.6}'.format(math.exp(total_loss / count_loss)))

        if (epoch + 1) % save_checkpoint_epoch == 0:
            torch.save(model, f'models/rnnlm_model_epoch{epoch + 1}.ckpt')


def test_rnnlm(select_model_path):
    model = torch.load(select_model_path, map_location="cpu")  # load the selected model

    # load the test data
    all_test_batch, all_test_target = give_valid_test.give_test(word2number_dict, n_step)
    total_test = len(all_test_target) * 128
    model.eval()
    criterion = nn.CrossEntropyLoss()
    total_loss = 0
    count_loss = 0
    for test_batch, test_target in zip(all_test_batch, all_test_target):
        test_output = model(test_batch)
        test_loss = criterion(test_output, test_target)
        total_loss += test_loss.item()
        count_loss += 1

    print(f"Test {total_test} samples with {select_model_path}……………………")
    print('lost =', '{:.6f}'.format(total_loss / count_loss),
          'ppl =', '{:.6}'.format(math.exp(total_loss / count_loss)))


if __name__ == '__main__':
    n_step = 5  # number of cells(= number of Step)
    n_hidden = 5  # number of hidden units in one cell
    batch_size = 512  # batch size
    learn_rate = 0.001
    all_epoch = 200  # the all epoch for training
    emb_size = 128  # embeding size
    save_checkpoint_epoch = 100  # save a checkpoint per save_checkpoint_epoch epochs
    train_path = 'data/train.txt'  # the path of train dataset

    word2number_dict, number2word_dict = make_dict(train_path)  # use the make_dict function to make the dict
    print("The size of the dictionary is:", len(word2number_dict))

    n_class = len(word2number_dict)  # n_class (= dict size)

    all_input_batch, all_target_batch = make_batch(train_path, word2number_dict, batch_size, n_step)  # make the batch
    print("The number of the train batch is:", len(all_input_batch))

    all_input_batch = torch.LongTensor(all_input_batch).to(device)  # list to tensor
    all_target_batch = torch.LongTensor(all_target_batch).to(device)

    print("\nTrain the RNNLM……………………")
    train_rnnlm()

    # print("\nTest the RNNLM……………………")
    # select_model_path = "models/rnnlm_model_epoch2.ckpt"
    # test_rnnlm(select_model_path)