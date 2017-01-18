import {UPDATE_ACHIEVEMENTS_LIST, UPDATE_OWN_CHARACTERS_LIST} from "../../src/player/actions";
import {updateAchievementsList, updateOwnCharactersList} from "../../src/player/actions";

describe('(player) actionCreators', () => {
  it('Should create an action object for updateAchievementsList.', () => {
    expect(updateAchievementsList([])).to.deep.equal({
      type: UPDATE_ACHIEVEMENTS_LIST,
      achievementsList: [],
    });
  });

  it('Should create an action object for updateOwnCharactersList.', () => {
    expect(updateOwnCharactersList([{id: 4, name: "abc"}])).to.deep.equal({
      type: UPDATE_OWN_CHARACTERS_LIST,
      charactersList: [{id: 4, name: "abc"}],
    });
  });
});
