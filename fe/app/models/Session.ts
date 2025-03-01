import { ObjectId } from "mongodb";
import { ServiceFactory } from "../services/ServiceFactory";
import { SessionService } from "../services/SessionService";

export class Session {

    private sessionService?: SessionService;
    private sessionId: string;
    private userId: string;
    private flow_duration_preference: number;
    private break_preference: number;
    private last_goal: string;
    private standard_picture: string;
    private pose_data: any;
    private tab_usage: any;
    private analysis: string;

    constructor(userId: string, flow_duration_preference: number, break_preference: number, last_goal: string, standard_picture: string, pose_data: any, tab_usage: any, analysis: string, sessionId?: string) {
        
        if (!sessionId) {
            this.sessionId = new ObjectId().toHexString();
        }
        else this.sessionId = sessionId;
        this.userId = userId;
        this.flow_duration_preference = flow_duration_preference;
        this.break_preference = break_preference;
        this.last_goal = last_goal;
        this.standard_picture = standard_picture;
        this.pose_data = pose_data;
        this.tab_usage = tab_usage;
        this.analysis = analysis;
    }

    public getSessionId(): string {
        return this.sessionId;
    }

    public getUserId(): string {
        return this.userId;
    }

    public getFlowDurationPreference(): number {
        return this.flow_duration_preference;
    }

    public getBreakPreference(): number {
        return this.break_preference;
    }

    public getLastGoal(): string {
        return this.last_goal;
    }

    public getStandardPicture(): string {
        return this.standard_picture;
    }

    public getPoseData(): any {
        return this.pose_data;
    }

    public getTabUsage(): any {
        return this.tab_usage;
    }

    public getAnalysis(): string {
        return this.analysis;
    }

    public setSessionId(sessionId: string) {
        this.sessionId = sessionId;
    }

    public setUserId(userId: string) {
        this.userId = userId;
    }

    public setFlowDurationPreference(flow_duration_preference: number) {
        this.flow_duration_preference = flow_duration_preference;
    }

    public setBreakPreference(break_preference: number) {
        this.break_preference = break_preference;
    }

    public setLastGoal(last_goal: string) {
        this.last_goal = last_goal;
    }

    public setStandardPicture(standard_picture: string) {
        this.standard_picture = standard_picture;
    }

    public setPoseData(pose_data: any) {
        this.pose_data = pose_data;
    }

    public setTabUsage(tab_usage: any) {
        this.tab_usage = tab_usage;
    }

    public setAnalysis(analysis: string) {
        this.analysis = analysis;
    }

    public async save() {
        if (!this.sessionService) {
            this.sessionService = await ServiceFactory.getSessionService();
        }
        this.sessionService.save(this);
    }

}