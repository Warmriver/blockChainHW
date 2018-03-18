import hashlib
import random
import time

# 区块链中交易
class Transaction:
    def __init__(self, from_addr, to_addr, amount):
        """
        fromAddr: 交易的发起人的地址
        toAdddr: 交易的收款人的地址
        amount: 交易金额
        """
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.amount = amount
    def __str__(self):
        return str(self.from_addr) + " send " + str(self.amount) + " to " + str(self.to_addr)

class Block:
    def __init__(self, transactions, timestamp, data = '', previous_hash = '0', nonce = 0):
        """
        transactions:交易列表，实际应用时并不能这么传递，因为交易的量很很大
        timestamp:时间戳
        data:数据
        nonce:随机数，使用这个数字的改变来更改block的hash值
        previous_hash:上一个模块的hash值
        hash:模块的hash值
        """
        self.transactions = transactions
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_block_hash()
        
    # 计算hash值，上一个block的hash值也在材料中
    def calculate_block_hash(self):
        combination = str(self.timestamp) + str(self.data) + str(self.previous_hash) + str(self.nonce)        
        for trans in self.transactions:
            combination += str(trans)
        return hashlib.sha256(bytes(combination,'utf-8')).hexdigest()
    # 挖掘，为了限制用户节点的挖掘能力，增加proof of work机制，增加挖掘的难度，difficulty越大，hash碰撞越难
    def mineblock(self,difficult):
        start = 0
        while [v for v in self.hash[start:difficult]] != ['0' for v in range(start, difficult)]:
        # while [v for v in self.hash[start:difficult]] != ['0' for v in range(start, difficult)]:
            self.nonce += 1
            self.hash = self.calculate_block_hash()
        print("挖到了一个 block，"+self.hash+",difficulty为", difficult)
# 区块链
class BlockChain:
    def __init__(self):
        """
        diffculty:难度
        chain:区块链，这里用数组表示
        pending_transactions:等待被挖掘的交易列表
        reward_coin:奖励金，对记账用户的奖励，即区块链货币，设置为一个block奖励1.2个，
                    单一用户修改此项并不会生效，因为每个人都有账本，必须说服多数派，拥有大于百分之50的同意。
        """
        self.difficult = 3
        self.chain = [self.genesis_block()]
        self.pending_transactions = []
        self.reward_coin = 1.2
    # 创世块
    def genesis_block(self):
        first_transaction = Transaction("24monkey", "24monkey", 50)
        return Block([first_transaction], int(time.time()),"创世模块")
    # 获得区块链最新的block
    def get_latest_block(self):
        return self.chain[len(self.chain) - 1]
    # 记录交易
    def transaction_record(self, transaction):
        self.pending_transactions.append(transaction)
    # 对区块链中行为进行交易，mining
    def mine_pending_transactions(self, reward_addr):
        new_block = Block(self.pending_transactions, int(time.time()), )
        new_block.mineblock(self.difficult)
        print("成功记录一笔交易，挖到了一个block")
        self.chain.append(new_block)
        self.pending_transactions = [Transaction('', reward_addr, self.reward_coin)]
    # 增加block
    def add_block(self, block):
        block.previous_hash = self.get_latest_block().hash
        block.mineblock(self.difficult)
        self.chain.append(block)
    # 获得一个账户的balance
    def get_balance(self, addr):
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction.from_addr == addr:
                    balance -= transaction.amount
                elif transaction.to_addr == addr:
                    balance += transaction.amount
        return balance
    # 账本是否本篡改，篡改者需要篡改所有的block且说服他人，篡改很困难
    def check_chain_validity(self):
        for i in range(1,len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            if(current_block.hash != current_block.calculate_block_hash()):
                return False
            if(current_block.previous_hash != previous_block.hash):
                return False
        return True
def time_s():
    return int(time.time())


if __name__ == '__main__':
    # 初始化一个区块链
    vin_coin = BlockChain()
    # 两笔交易
    trans_a = Transaction("shiki_addr", "vincent_addr", 44)
    trans_b = Transaction("vincent_addr", "shiki_addr", 44)
    """
    测试挖矿，proof of work的难度测试
    """
    vin_coin.add_block(Block([trans_a], time_s(), {" reason " : " I owed you"}))
    vin_coin.add_block(Block([trans_b], time_s(), {" reason " : " I gave it back to you cause I love you"}))
    """
    测试篡改数据的测试
    """
    print("vin币chain合法吗？", vin_coin.check_chain_validity())
    vin_coin.chain[1].transactions[0].amount = 40
    # 修改一个block后，重新计算这个block的hash，并不能成功
    vin_coin.chain[1].hash = vin_coin.chain[1].calculate_block_hash()
    print("vin币chain合法吗？", vin_coin.check_chain_validity())

    """
    测试vin币奖励机制
    """
    vin_coin.transaction_record(trans_a)
    vin_coin.transaction_record(trans_b)
    vin_coin.mine_pending_transactions("记录者1")
    # 由于记录者1获得奖励的事件还没有入账，所以查不到
    print("记录者1的账户: ", vin_coin.get_balance("记录者1"))
    # 记录者2确认了记录者1的行为，记录者1的账户余额不足
    vin_coin.mine_pending_transactions("记录者2")
    print("记录者1的账户: ", vin_coin.get_balance("记录者1"))
