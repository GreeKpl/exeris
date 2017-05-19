import {connect} from "react-redux";
import MyCharacterPage from "./MyCharacterPage";
import {requestMyCharacterInfo} from "../../../modules/myCharacter";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.params.characterId,
    isSmall: state.get("browser").atMost.small,
  };
};

const mapDispatchToProps = (dispatch, ownProps) => {
  return {
    requestState: () => dispatch(requestMyCharacterInfo(ownProps.params.characterId)),
  }
};

const MyCharacterPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(MyCharacterPage);

export default MyCharacterPageContainer;
