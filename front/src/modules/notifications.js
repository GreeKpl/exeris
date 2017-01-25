import * as Immutable from "immutable";
import socket from "../util/server";

export const ADD_NOTIFICATION = "exeris-front/notifications/ADD_NOTIFICATION";
export const START_LOADING_NOTIFICATIONS = "exeris-front/notifications/START_LOADING_NOTIFICATIONS";


export const setUpSocketioListeners = dispatch => {
  socket.on("player.new_notification", notification => {
    dispatch(addNotification([notification]));
  });
};

export const requestMissingNotifications = () => {
  return (dispatch, getState) => {
    if (!alreadyStartedLoading(fromNotificationsState(getState()))) {
      dispatch(startLoading());

      socket.request("player.request_all_notifications");
    }
  }
};

export const startLoading = () => {
  return {
    type: START_LOADING_NOTIFICATIONS,
  };
};

export const addNotification = notification => {
  return {
    type: ADD_NOTIFICATION,
    notification: notification,
  };
};


export const notificationsReducer = (state = Immutable.fromJS(
  {
    list: [],
    startedLoading: false,
  }), action) => {
  switch (action.type) {
    case START_LOADING_NOTIFICATIONS:
      return state.set("startedLoading", true);
    case ADD_NOTIFICATION:
      return state.updateIn(["list"], list => list.push(Immutable.fromJS(action.notification)));
    default:
      return state;
  }
};

export const getCharacterAndPlayerNotifications = (state, characterId) => {
  const notificationsList = state.get("list", Immutable.List());
  const playerOrActiveCharacter = Immutable.Set([characterId, "0"]);
  return notificationsList.filter(notification => playerOrActiveCharacter.has(notification.get("characterId")));
};

export const alreadyStartedLoading = state =>
  state.get("startedLoading");

export const fromNotificationsState = (state) =>
  state.get("notifications", Immutable.Map());
