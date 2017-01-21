import {connect} from "react-redux";
import MyCharacterPage from "./MyCharacterPage";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.params.characterId};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const MyCharacterPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(MyCharacterPage);

export default MyCharacterPageContainer;
