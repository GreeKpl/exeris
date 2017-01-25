import {
  addNotification,
  getCharacterAndPlayerNotifications,
  alreadyStartedLoading,
  startLoading,
  notificationsReducer
} from "../../src/modules/notifications";
import * as Immutable from "immutable";

describe('(notifications) notificationsReducer', () => {

  it('Should initialize with initial state of empty list.', () => {
    expect(notificationsReducer(undefined, {})).to.equal(Immutable.fromJS({
      list: [],
      startedLoading: false,
    }));
  });

  it('Should return the previous state if an action was not matched.', () => {
    const previousState = Immutable.fromJS({
      list: [],
      startedLoading: false,
    });
    let state = notificationsReducer(previousState, {});
    expect(state).to.equal(previousState);
  });


  it('Should change state of startedLoading flag.', () => {
    const previousState = Immutable.fromJS({
      list: [],
      startedLoading: false,
    });
    expect(alreadyStartedLoading(previousState)).to.equal(false);

    const state = notificationsReducer(previousState, startLoading());
    expect(state).to.equal(Immutable.fromJS({
      list: [],
      startedLoading: true,
    }));

    expect(alreadyStartedLoading(state)).to.equal(true);
  });

  it('Should be able to store and read notifications.', () => {
    let state = Immutable.fromJS({
      list: [],
      startedLoading: false,
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
    }));

    expect(getCharacterAndPlayerNotifications(state, "TAK")).to.equal(Immutable.fromJS([
      {"id": 1, "characterId": "TAK"},
      {"id": 3, "characterId": "0"},
    ]));

    expect(getCharacterAndPlayerNotifications(state, null)).to.equal(Immutable.fromJS([
      {"id": 3, "characterId": "0"},
    ]));
  });
});
