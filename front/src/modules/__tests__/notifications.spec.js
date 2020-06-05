import {
  addNotification,
  getCharacterAndPlayerNotifications,
  alreadyStartedLoading,
  startLoading,
  getVisibleNotification,
  notificationsReducer,
  removeNotification,
  showNotificationDialog,
  hideNotificationDialog,
  selectNotificationOption,
  requestShowNotification,
  requestMissingNotifications,
  __RewireAPI__ as notificationsRewire,
  START_LOADING_NOTIFICATIONS,
  SHOW_NOTIFICATION_DIALOG,
  REMOVE_NOTIFICATION,
  HIDE_NOTIFICATION_DIALOG
} from "../notifications";
import * as Immutable from "immutable";
import {createMockStore, DependenciesStubber} from "../../../tests/testUtils";

describe('(notifications) notificationsReducer', () => {

  it('Should initialize with initial state of empty list.', () => {
    expect(notificationsReducer(undefined, {})).toEqual(Immutable.fromJS({
      list: [],
      startedLoading: false,
      visibleNotification: Immutable.Map(),
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      list: [],
      startedLoading: false,
      visibleNotification: Immutable.Map(),
    });
    let state = notificationsReducer(previousState, {});
    expect(state).toEqual(previousState);
  });


  it('Should change state of startedLoading flag.', () => {
    const previousState = Immutable.fromJS({
      list: [],
      startedLoading: false,
      visibleNotification: Immutable.Map(),
    });
    expect(alreadyStartedLoading(previousState)).toEqual(false);

    const state = notificationsReducer(previousState, startLoading());
    expect(state).toEqual(Immutable.fromJS({
      list: [],
      startedLoading: true,
      visibleNotification: Immutable.Map(),
    }));

    expect(alreadyStartedLoading(state)).toEqual(true);
  });

  it('Should be able to store and read notifications.', () => {
    let state = Immutable.fromJS({
      list: [],
      startedLoading: false,
      visibleNotification: Immutable.Map(),
    });

    state = notificationsReducer(state,
      addNotification({"id": 1, "characterId": "TAK"}
      ));
    state = notificationsReducer(state,
      addNotification({"id": 3, "characterId": "0"}
      ));
    state = notificationsReducer(state,
      addNotification({"id": 7, "characterId": "NIE"}
      ));


    expect(state).toEqual(Immutable.fromJS({
      list: [
        {"id": 1, "characterId": "TAK"},
        {"id": 3, "characterId": "0"},
        {"id": 7, "characterId": "NIE"},
      ],
      startedLoading: false,
      visibleNotification: Immutable.Map(),
    }));

    expect(getCharacterAndPlayerNotifications(state, "TAK")).toEqual(Immutable.fromJS([
      {"id": 1, "characterId": "TAK"},
      {"id": 3, "characterId": "0"},
    ]));

    expect(getCharacterAndPlayerNotifications(state, null)).toEqual(Immutable.fromJS([
      {"id": 3, "characterId": "0"},
    ]));

    state = notificationsReducer(state, removeNotification(7));
    expect(getCharacterAndPlayerNotifications(state, "NIE")).toEqual(Immutable.fromJS([
      {"id": 3, "characterId": "0"},
    ]));
  });

  it('Should be able to show and hide notification dialog.', () => {
    let state = Immutable.fromJS({
      list: [],
      startedLoading: false,
      visibleNotification: Immutable.Map(),
    });

    expect(getVisibleNotification(state)).toEqual(Immutable.Map());

    state = notificationsReducer(state, showNotificationDialog({
      id: "hehehe",
      options: [],
      title: "HEHE"
    }));
    expect(getVisibleNotification(state)).toEqual(Immutable.fromJS({
      id: "hehehe",
      options: [],
      title: "HEHE"
    }));

    state = notificationsReducer(state, hideNotificationDialog());
    expect(getVisibleNotification(state)).toEqual(Immutable.Map());
  });

  describe("Asynchronous socketio actions", () => {
    const charId = "DEF";

    it('Should request the notifications list when it is not loaded.', () => {

      const store = createMockStore(Immutable.fromJS({
        notifications: {
          startedLoading: false,
        },
      }), null);

      store.dispatch(requestMissingNotifications());
      store.socketCalledWith("player.request_all_notifications");

      const actions = store.getActions();
      expect(actions).toHaveLength(1);
      expect(actions[0]).toEqual({
        type: START_LOADING_NOTIFICATIONS,
      });
    });
  });

  it('Should request the notifications list when it is loaded.', () => {
    const store = createMockStore(Immutable.fromJS({
      notifications: {
        startedLoading: true,
      },
    }), null);

    store.dispatch(requestMissingNotifications());

    store.socketNotCalled();
    const actions = store.getActions();
    expect(actions).toHaveLength(0);
  });

  it('Should request the info about notification.', () => {
    const notificationId = "ALECOTO";
    const notification = {
      id: notificationId,
      title: "Notification title",
      text: "This is notification",
    };
    const store = createMockStore({}, [notification]);

    store.dispatch(requestShowNotification(notificationId));

    store.socketCalledWith("player.show_notification", notificationId);
    const actions = store.getActions();
    expect(actions).toHaveLength(1);
    expect(actions[0]).toEqual({
      type: SHOW_NOTIFICATION_DIALOG,
      notification: notification,
    });
  });


  it('Should request executing the notification option.', () => {
    const notificationId = "ALECOTO";
    const endpoint = "close_notification";
    const params = ["A", "B", "C"];
    const notificationOption = {
      notificationId: notificationId,
      endpoint: endpoint,
      params: params,
    };

    const store = createMockStore({}, []);
    store.dispatch(selectNotificationOption(notificationOption));

    store.socketCalledWith(endpoint, ...params);
    const actions = store.getActions();
    expect(actions).toHaveLength(2);
    expect(actions[0]).toEqual({
      type: HIDE_NOTIFICATION_DIALOG,
    });
    expect(actions[1]).toEqual({
      type: REMOVE_NOTIFICATION,
      notificationId: notificationId,
    });

  });
});
