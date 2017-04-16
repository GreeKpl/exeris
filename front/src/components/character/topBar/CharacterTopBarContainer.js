import {connect} from "react-redux";
import CharacterTopBar from "./CharacterTopBar";
import {getMyCharacterInfoFromMyCharacterState, requestMyCharacterInfo} from "../../../modules/myCharacter";

const mapStateToProps = (state, ownProps) => {
  const myCharacterInfo = getMyCharacterInfoFromMyCharacterState(state, ownProps.characterId);
  return {
    characterId: ownProps.characterId,
    activePage: ownProps.activePage,
    workIntent: myCharacterInfo.get("workIntent"),
    combatIntent: myCharacterInfo.get("combatIntent"),
    hunger: myCharacterInfo.getIn(["states", "hunger"]),
    damage: myCharacterInfo.getIn(["states", "damage"]),
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    requestState: () => dispatch(requestMyCharacterInfo(ownProps.characterId)),
  }
};

const CharacterTopBarContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(CharacterTopBar);

export default CharacterTopBarContainer;
