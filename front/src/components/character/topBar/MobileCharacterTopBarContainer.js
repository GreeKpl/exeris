import {connect} from "react-redux";
import MobileCharacterTopBar from "./MobileCharacterTopBar";
import {getMyCharacterInfoFromMyCharacterState, requestMyCharacterInfo} from "../../../modules/myCharacter";
import {fromPlayerState, getOwnCharactersList} from "../../../modules/player";

const mapStateToProps = (state, ownProps) => {
  const myCharacterInfo = getMyCharacterInfoFromMyCharacterState(state, ownProps.characterId);
  return {
    characterId: ownProps.characterId,
    characterIdsList: getOwnCharactersList(fromPlayerState(state)),
    activePage: ownProps.activePage,
    mainPageActive: false,
    characterActivePage: ownProps.characterActivePage,
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

const MobileCharacterTopBarContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(MobileCharacterTopBar);

export default MobileCharacterTopBarContainer;
