export interface SessionDocument {
    sessionId: string;
    userId: string;
    flow_duration_preference: number;
    break_preference: number;
    last_goal: string;
    standard_picture: string;
    pose_data: any;
    tab_usage: any;
    analysis: string;
}