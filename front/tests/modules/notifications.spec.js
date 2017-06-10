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
} from "../../src/modules/notifications";
import * as Immutable from "immutable";
import {createMockStore, DependenciesStubber} from "../testUtils";

describe('(notifications) notificationsReducer', () => {

  it('Should initialize with initial state of empty list.', () => {
    expect(notificationsReducer(undefined, {})).to.equal(Immutable.fromJS({
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
    expect(state).to.equal(previousState);
  });


  it('Should change state of startedLoading flag.', () => {
    const previousState = Immutable.fromJS({
      list: [],
      startedLoading: false,
      visibleNotification: Immutable.Map(),
    });
    expect(alreadyStartedLoading(previousState)).to.equal(false);

    const state = notificationsReducer(previousState, startLoading());
    expect(state).to.equal(Immutable.fromJS({
      list: [],
      startedLoading: true,
      visibleNotification: Immutable.Map(),
    }));

    expect(alreadyStartedLoading(state)).to.equal(true);
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


    expect(state).to.equal(Immutable.fromJS({
      list: [
        {"id": 1, "characterId": "TAK"},
        {"id": 3, "characterId": "0"},
        {"id": 7, "characterId": "NIE"},
      ],
      startedLoading: false,
      visibleNotification: Immutable.Map(),
    }));

    expect(getCharacterAndPlayerNotifications(state, "TAK")).to.equal(Immutable.fromJS([
      {"id": 1, "characterId": "TAK"},
      {"id": 3, "characterId": "0"},
    ]));

    expect(getCharacterAndPlayerNotifications(state, null)).to.equal(Immutable.fromJS([
      {"id": 3, "characterId": "0"},
    ]));

    state = notificationsReducer(state, removeNotification(7));
    expect(getCharacterAndPlayerNotifications(state, "NIE")).to.equal(Immutable.fromJS([
      {"id": 3, "characterId": "0"},
    ]));
  });

  it('Should be able to show and hide notification dialog.', () => {
    let state = Immutable.fromJS({
      list: [],
      startedLoading: false,
      visibleNotification: Immutable.Map(),
    });

    expect(getVisibleNotification(state)).to.equal(Immutable.Map());

    state = notificationsReducer(state, showNotificationDialog({
      id: "hehehe",
      options: [],
      title: "HEHE"
    }));
    expect(getVisibleNotification(state)).to.equal(Immutable.fromJS({
      id: "hehehe",
      options: [],
      title: "HEHE"
    }));

    state = notificationsReducer(state, hideNotificationDialog());
    expect(getVisibleNotification(state)).to.equal(Immutable.Map());
  });

  describe("Asynchronous socketio actions", () => {
    const charId = "DEF";

    it('Should request the notifications list when it is not loaded.', () => {

      const dependencies = new DependenciesStubber(notificationsRewire, {
        alreadyStartedLoading: () => false,
        fromNotificationsState: () => 123,
      });
      const store = createMockStore({}, null);
      dependencies.rewireAll();

      store.dispatch(requestMissingNotifications());
      store.socketCalledWith("player.request_all_notifications");

      const actions = store.getActions();
      expect(actions).to.have.length(1);
      expect(actions[0]).to.deep.equal({
        type: START_LOADING_NOTIFICATIONS,
      });

      dependencies.unwireAll();
    });
  });

  it('Should request the notifications list when it is loaded.', () => {
    const dependencies = new DependenciesStubber(notificationsRewire, {
      alreadyStartedLoading: () => true,
      fromNotificationsState: () => 123,
    });
    const store = createMockStore({}, null);
    dependencies.rewireAll();

    store.dispatch(requestMissingNotifications());

    store.socketNotCalled();
    const actions = store.getActions();
    expect(actions).to.have.length(0);

    dependencies.unwireAll();
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
    expect(actions).to.have.length(1);
    expect(actions[0]).to.deep.equal({
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
    expect(actions).to.have.length(2);
    expect(actions[0]).to.deep.equal({
      type: HIDE_NOTIFICATION_DIALOG,
    });
    expect(actions[1]).to.deep.equal({
      type: REMOVE_NOTIFICATION,
      notificationId: notificationId,
    });

  });
});
