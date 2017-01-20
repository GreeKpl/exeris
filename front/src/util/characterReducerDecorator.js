import * as Immutable from "immutable";
/**
 * Decorator allows having multiple state subtrees for a single reducer - each reacting
 * for actions which specify the specific `characterId` key.
 *
 * All keys are converted to string.
 *
 * Example state:
 * {"a": 1,
 *  "b": 2,
 *  "c": 5,
 * }
 *
 * After executing reducer for action {type: INCREMENT, characterId: "b"}:
 * {"a": 1,
 *  "b": 3,
 *  "c": 5,
 * }
 *
 * @param reducer
 * @returns function composing multiple reducers, each for each key of state
 */

export const characterReducerDecorator = (reducer) => {
  return (state = Immutable.Map(), action) => {
    if ("characterId" in action) {
      const characterId = String(action.characterId);

      // if there's no such key then reducer's initial value is used
      const newValue = reducer(state.get(characterId), action);
      return state.set(characterId, newValue);
    }
    return state;
  };
};
