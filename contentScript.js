(() => {
  let youtubeLeftControls, youtubePlayer;
  let currentVideo = "";
  let allComments = [];


  async function getCommentCounts(videoId) {
    // THe result shoould come here, from the API
    let positiveCounts = 10;
    let negativeCounts = 30;
    let neutralCounts = 40;
    console.log("Returning count for video", videoId);
  
   
  
    return { positiveCounts, negativeCounts, neutralCounts };
  }

  function getCommentsFromLocalStorage(callback) {
    chrome.storage.local.get('comments', (data) => {
      if (chrome.runtime.lastError) {
        console.error(chrome.runtime.lastError.message);
        return;
      }
      callback(data.comments || {});
    });
  }

  function saveCommentsToLocalStorage(comments) {
    chrome.storage.local.set({ 'comments': comments }, () => {
      console.log('Comments saved to local storage', comments);
    });
  }

    chrome.runtime.onMessage.addListener((obj, sender, response) => {
    const { type, value, videoId } = obj;
    console.log("Received message", obj);
    if (type === "NEW") {
      currentVideo = videoId;
      getCommentsFromLocalStorage((comments) => {
        allComments = comments;
        console.log('All comments fetched on startup:', allComments);
        if (allComments[videoId] === undefined) {
          getCommentCounts(videoId).then(({ positiveCounts, negativeCounts, neutralCounts }) => {
            const newComments = { positiveCounts, negativeCounts, neutralCounts };
            const updatedAllComments = { ...allComments, [videoId]: newComments };
            console.log('Updated all comments:', updatedAllComments);
            saveCommentsToLocalStorage(updatedAllComments);
          });
        }
      });
      
      
    } 
  });

  
})();

