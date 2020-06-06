import {connect} from "react-redux";
import {requestAchievementsList, getAchievementsList, fromPlayerState} from "../../modules/player";
import React from "react";
import {ListGroup, ListGroupItem, Panel} from "react-bootstrap";

const AchievementEntry = ({title, children}) => (
  <ListGroupItem header={title}>
    {children}
  </ListGroupItem>
);

class AchievementsList extends React.Component {
  componentDidMount() {
    this.props.onMount();
  }

  render() {
    return <Panel header="Achievements">
      <ListGroup>
        {this.props.achievements.map(achievement =>
          <AchievementEntry key={achievement.get("title")}
                            title={achievement.get("title")}>
            {achievement.get("content")}
          </AchievementEntry>
        )}
      </ListGroup>
    </Panel>;
  }
}

export {AchievementsList};

const mapStateToProps = (state) => {
  return {achievements: getAchievementsList(fromPlayerState(state))};
};

const mapDispatchToProps = (dispatch) => {
  return {
    onMount: () => dispatch(requestAchievementsList()),
  }
};

const AchievementsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(AchievementsList);

export default AchievementsListContainer;
