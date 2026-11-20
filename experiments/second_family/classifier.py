"""Two-path CNN-F, adapted to the two event families and sparse terminals."""

import copy
import numpy as np
import torch
from torch import nn
from shared import HERE, RESULT, TMP, digest, save


class Pathway(nn.Sequential):
    def __init__(self, columns):
        super().__init__(
            nn.Conv2d(1, 4, (2, 1)),
            nn.BatchNorm2d(4),
            nn.ReLU(),
            nn.MaxPool2d((2, 1)),
            nn.Conv2d(4, 8, (2, 1)),
            nn.BatchNorm2d(8),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(24 * columns, 16),
            nn.ReLU(),
        )


class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.eigen = Pathway(3)
        self.singular = Pathway(2)
        self.output = nn.Linear(32, 2)
        for m in self.modules():
            if isinstance(m, (nn.Conv2d, nn.Linear)):
                nn.init.xavier_uniform_(m.weight)
                nn.init.zeros_(m.bias)

    def forward(self, eigen, singular):
        return self.output(torch.cat((self.eigen(eigen), self.singular(singular)), dim=1))


def load_split(name):
    with np.load(TMP / (name + ".npz")) as z:
        return [torch.tensor(z[k])[:, None] for k in ("eigen", "singular")], torch.tensor(z["y"]).long()


def train():
    if (RESULT / "freeze.json").exists():
        raise RuntimeError("Training closed")
    torch.set_num_threads(1)
    x, y = load_split("train")
    v, w = load_split("val")
    means = [a.mean(0, keepdim=True) for a in x]
    scales = [a.std(0, keepdim=True).clamp_min(1e-6) for a in x]
    x = [(a - b) / s for a, b, s in zip(x, means, scales)]
    v = [(a - b) / s for a, b, s in zip(v, means, scales)]
    loss = nn.CrossEntropyLoss()
    runs = []
    best = None
    for seed in (19, 37, 101):
        torch.manual_seed(seed)
        net = CNN()
        opt = torch.optim.RMSprop(net.parameters(), lr=0.001, alpha=0.9, weight_decay=0.001)
        best_loss = float("inf")
        for epoch in range(180):
            net.train()
            for ids in torch.randperm(len(y)).split(30):
                opt.zero_grad()
                loss(net(x[0][ids], x[1][ids]), y[ids]).backward()
                opt.step()
            net.eval()
            with torch.no_grad():
                logits = net(*v)
                current = loss(logits, w).item()
            if current < best_loss:
                best_loss, best_epoch = current, epoch
                state = copy.deepcopy(net.state_dict())
                correct = int((logits.argmax(1) == w).sum())
            if epoch - best_epoch >= 12:
                break
        runs.append(dict(seed=seed, epoch=best_epoch + 1, validation_loss=best_loss, correct=correct))
        if best is None or best_loss < best[0]:
            best = (best_loss, seed, state)
    torch.save(dict(weights=best[2], means=means, scales=scales), HERE / "cnn.pt")
    save(
        RESULT / "training.json",
        dict(
            training=360,
            validation=108,
            chosen_seed=best[1],
            runs=runs,
            features={k: digest(TMP / (k + ".npz")) for k in ("train", "val")},
        ),
    )
    print(runs, flush=True)


class Predict:
    def __init__(self):
        torch.set_num_threads(1)
        state = torch.load(HERE / "cnn.pt", map_location="cpu", weights_only=True)
        self.model = CNN().eval()
        self.model.load_state_dict(state["weights"])
        self.means, self.scales = state["means"], state["scales"]

    @torch.no_grad()
    def __call__(self, features):
        x = [
            (torch.as_tensor(z)[None, None] - m) / s for z, m, s in zip(features, self.means, self.scales)
        ]
        return ("load", "line")[self.model(*x).argmax().item()]


if __name__ == "__main__":
    train()
