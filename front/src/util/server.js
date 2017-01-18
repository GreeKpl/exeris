import io from "socket.io-client";


const getDeprecatedQueryString = () => {
  const href = window.location.href;
  const parts = /character\/\d+/.exec(href);
  let characterId = "";
  if (parts) {
    characterId = parts[1];
  }

  return {
    query: "character_id=" + characterId + "&blueprint=character&language=en",
  }
};

const socket = io.connect('//' + window.location.hostname + ':' + window.location.port,
  getDeprecatedQueryString()
); // TODO temporarily needed for old, server-side templates

// create request which turns "acknowledgement callback" into "on success callback"

socket.request = function () {
  const args = Array.prototype.slice.call(arguments);
  const lastIndex = args.length - 1;
  if (typeof args[lastIndex] === "function") { // there is a callback
    const originalCallback = args[lastIndex];
    args[lastIndex] = function () {
      const callbackArgs = Array.prototype.slice.call(arguments, 1);
      const wasSuccessful = arguments[0];
      if (wasSuccessful) { // emit was successful, so run the original callback
        originalCallback.apply(this, callbackArgs);
      }
    };
  }
  socket.emit.apply(this, args);
};


export default socket;
