import io from "socket.io-client";


const setupSocketio = () => {
  const socket = io.connect('//' + window.location.hostname + ':' + window.location.port);

  socket.on("reset_connection", () => {
    socket.io.disconnect();
    socket.io.reconnect();
  });

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
  return socket;
}


export default setupSocketio;
