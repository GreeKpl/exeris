import {connect} from "react-redux";
import {getMyCharacterInfoFromMyCharacterState} from "../../../modules/myCharacter";
import * as Immutable from "immutable";
import IntentsList from "./IntentsList";

const mapStateToProps = (state, ownProps) => {

  const myCharacterInfo = getMyCharacterInfoFromMyCharacterState(state, ownProps.characterId);
  return {
    characterId: ownProps.characterId,
    intents: myCharacterInfo.get("allIntents", Immutable.List()),
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const IntentsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(IntentsList);

export default IntentsListContainer;
