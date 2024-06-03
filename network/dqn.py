import torch


class DuelingDQN(torch.nn.Module):

    def __init__(self, state_size=8, action_size=4, hidden_size=64, outputs=1):
        super(DuelingDQN, self).__init__()

        # Common layers
        self.layer1 = torch.nn.Linear(state_size, hidden_size)
        self.layer2 = torch.nn.Linear(hidden_size, hidden_size)

        # Advantage layer
        self.advantage = torch.nn.Linear(hidden_size, action_size)

        # Value layer
        self.value = torch.nn.Linear(hidden_size, outputs)

    def forward(self, state):
        # Common part of the network
        x = torch.relu(self.layer1(state))
        x = torch.sigmoid(self.layer2(x))

        # Streams split here
        advantage = self.advantage(x)
        value = self.value(x)

        # Recombine advantage and value for Q
        return value + (advantage - advantage.max(dim=1, keepdim=True)[0])
