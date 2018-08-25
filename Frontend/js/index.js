tweetBase = `<div class="tweet flex justify-between">
<div class="tweet-pic circle border flex items-center justify-center">
    <i class="fa fa-user" aria-hidden="true"></i>
  </div>
  <div  class="tweet-content">
    <div class="flex justify-between">
      <div>
        <span class="name">
          An user
        </span>
      </div>
      <div class="when">
        -WHEN-
      </div>
    </div>
    <div class="actual-content">
      <p>
        -CONTENT-
      </p>
    </div>
  </div>
</div>`

tweets = document.getElementById("tweets");

function AddTweet(tweetList) {
  tweets.innerHTML = "";
  tweetList.forEach((value, index, array)=>{
    text = tweetBase.replace("-WHEN-", value.Time).replace("-CONTENT-", value.Tweet);
    tweets.innerHTML = text + tweets.innerHTML;
  });
}

var getJSON = function(url, callback) {
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url, true);
  xhr.responseType = 'json';
  xhr.onload = function() {
    var status = xhr.status;
    if (status === 200) {
      callback(null, xhr.response);
    } else {
      callback(status, xhr.response);
    }
  };
  xhr.send();
};

function sendPost(yourUrl)
{
  var xhr = new XMLHttpRequest();
  xhr.open("POST", yourUrl, true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({
    Tweet: document.getElementById("send-twit").value
  }));
  document.getElementById("send-twit").value = "";
}

var Tweets = [];

function SendClick()
{
  sendPost("http://localhost:5000/transactions/new");

  getJSON("http://localhost:5000/mine", (status, resp) =>{
    Tweets = [];
    getJSON("http://localhost:5000/tweets", (status, resp) =>{
      Tweets = resp;
      AddTweet(Tweets);
    })
  })
}


getJSON("http://localhost:5000/tweets", (status, resp) =>{
  Tweets = resp;
  AddTweet(Tweets);
})