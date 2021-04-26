# Voice Activity Detection
****
Uses LSTM with 12 MFCC features for each audio frame, (20) frames for LSTM predictions, and the result Input has a size of 12x20x1

Uses the default input device for streaming.

To run the flask app:

    pip3 install -r requirement.txt

    Install all missing dependencies

    cd env

    flask run


It has around 4000 nodes

Net(
    (relu): ReLU()
    (rnn): LSTM(12, 20, batch_first=True)
    (lin1): Linear(in_features=400, out_features=26, bias=True)
    (lin2): Linear(in_features=26, out_features=2, bias=True)
    (softmax): Softmax(dim=1)
)

    


