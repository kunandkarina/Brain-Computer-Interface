class SCCNet_v2(nn.Module):
    """Advanced SCCNet model without permutation layer.
    ... Parameters ............
    C: int
        Number of EEG input channels.
    N: int
        Number of EEG input time samples.
    nb_classes: int
        Number of classes to predict.
    Nu: int
        Number of spatial kernel.
    Nt: int
        Length of spatial kernel.
    Nc: int
        Number of spatial-temporal kernel.
    fs: float
        Sampling frequency of EEG input.
    dropoutRate: float
        Dropout ratio.
    ... References ............
    https://ieeexplore.ieee.org/document/8716937
    """
    def __init__(self, C, N, nb_classes, Nu=None, Nt=1, Nc=20, fs=1000.0, dropoutRate=0.5):
        super(SCCNet_v2, self).__init__()
        Nu = C if Nu is None else Nu
        # self.layer = ...
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_channels=1, out_channels=Nu, kernel_size=(C, Nt), padding=0),
            nn.BatchNorm2d(Nu),
            nn.ReLU(inplace=True)
        )

        self.conv2 = nn.Sequential(
            nn.Conv2d(in_channels=Nu, out_channels=Nc, kernel_size=(1, 12), padding=0),
            nn.BatchNorm2d(Nc),
            nn.ReLU(inplace=True)
        )

        self.dropout = nn.Dropout(dropoutRate)
        self.avgpool = nn.AvgPool2d(kernel_size=(1, 62), stride=(1, 12))

        fc_in_size = self.get_size(C, N)[1]
        self.classifier = nn.Linear(fc_in_size, nb_classes, bias=True)

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = x ** 2
        x = self.dropout(x)
        x = self.avgpool(x)
        x = torch.log(x)
        x = x.view(x.size()[0], -1)
        x = self.classifier(x)
        return x

    def get_size(self, C, N):
        data = torch.ones((1, 1, C, N))
        x = self.conv1(data)
        x = self.conv2(x)
        x = self.avgpool(x)
        x = x.view(x.size()[0], -1)
        return x.size()