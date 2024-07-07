

var raw = "this is a bad restaurant";

async function getSentiment(text){
  var myHeaders = new Headers();
    myHeaders.append("apikey", "AkuncbToeEdyyZ0QORkJlVkP0Hs0xY2U");
    var requestOptions = {
        method: 'POST',
        redirect: 'follow',
        headers: myHeaders,
        body: raw
      };
    const data= await fetch("https://api.apilayer.com/sentiment/analysis", requestOptions)
    .then(response => response.json());
    console.log(data)
    return data

}
const data = getSentiment(raw)
