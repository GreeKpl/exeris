import * as Immutable from "immutable";
import socket from "../util/server";

export const ADD_NOTIFICATION = "exeris-front/notifications/ADD_NOTIFICATION";
export const START_LOADING_NOTIFICATIONS = "exeris-front/notifications/START_LOADING_NOTIFICATIONS";
export const SHOW_NOTIFICATION_DIALOG = "exeris-front/notifications/SHOW_NOTIFICATION_DIALOG";
export const HIDE_NOTIFICATION_DIALOG = "exeris-front/notifications/HIDE_NOTIFICATION_DIALOG";
export const REMOVE_NOTIFICATION = "exeris-front/notifications/REMOVE_NOTIFICATION";


export const setUpSocketioListeners = dispatch => {
  socket.on("player.new_notification", notification => {
    dispatch(addNotification(notification));
  });

  socket.on("player.show_error", (characterId, errorMessage) => {
    if (!characterId) {
      characterId = "0";
    }
    const uniqueId = "error-" + Math.floor(Math.random() * 1e6);
    dispatch(addNotification({
      characterId: characterId,
      title: errorMessage,
      id: uniqueId,
      detailed: false,
      easyClose: true,
      type: "error",
    }));
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

export const removeNotification = notificationId => {
  return {
    type: REMOVE_NOTIFICATION,
    notificationId: notificationId,
  };
};

export const requestShowNotification = notificationId => {
  return dispatch => {
    socket.request("player.show_notification", notificationId, notification => {
      dispatch(showNotificationDialog(notification));
    });
  };
};

export const showNotificationDialog = (notification) => {
  return {
    type: SHOW_NOTIFICATION_DIALOG,
    notification: notification,
  };
};

export const hideNotificationDialog = () => {
  return {
    type: HIDE_NOTIFICATION_DIALOG,
  };
};

export const selectNotificationOption = notificationOption => {
  return dispatch => {
    socket.request(notificationOption.endpoint, ...notificationOption.params,
      () => {
        dispatch(hideNotificationDialog());
        dispatch(removeNotification(notificationOption.notificationId));
      });
  }
};

export const notificationsReducer = (state = Immutable.fromJS(
  {
    list: [],
    startedLoading: false,
    visibleNotification: Immutable.Map(),
  }), action) => {
  switch (action.type) {
    case START_LOADING_NOTIFICATIONS:
      return state.set("startedLoading", true);
    case ADD_NOTIFICATION:
      return state.update("list", list => list.push(Immutable.fromJS(action.notification)));
    case REMOVE_NOTIFICATION:
      return state.update("list", list => list.filter(item => item.get("id") != action.notificationId));
    case SHOW_NOTIFICATION_DIALOG:
      return state.set("visibleNotification", Immutable.fromJS(action.notification));
    case HIDE_NOTIFICATION_DIALOG:
      return state.set("visibleNotification", Immutable.Map());
    default:
      return state;
  }
};

export const getCharacterAndPlayerNotifications = (state, characterId) => {
  const notificationsList = state.get("list", Immutable.List());
  const playerOrActiveCharacter = Immutable.Set([characterId, "0"]);
  return notificationsList.filter(notification => playerOrActiveCharacter.has(notification.get("characterId")));
};

export const getVisibleNotification = state =>
  state.get("visibleNotification");


export const alreadyStartedLoading = state =>
  state.get("startedLoading");

export const fromNotificationsState = (state) =>
  state.get("notifications", Immutable.Map());
