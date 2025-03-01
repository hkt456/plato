import { Cookie } from "next/font/google";
import { User } from "../models/User";
import Database from "../repo/Database";
import { UserRepository } from "../repo/UserRepository";
import { CookieService } from "./CookieService";
import { UserService } from "./UserService";
import { UserServiceImpl } from "./UserServiceImpl";
import { CookieRepository } from "../repo/CookieRepository";
import { CookieServiceImpl } from "./CookieServiceImpl";
import { SessionService } from "./SessionService";
import { SessionServiceImpl } from "./SessionServiceImpl";
import { SessionRepository } from "../repo/SessionRepository";

export class ServiceFactory {

    private static userService: UserService;
    private static cookieService: CookieService;
    private static sessionService: SessionService;
    
    public static async getUserService(): Promise<UserService> {
        if (!ServiceFactory.userService) {
            ServiceFactory.userService = new UserServiceImpl(new UserRepository(await Database.getCollection("users")));
        }
        return ServiceFactory.userService;
    }

    public static async getCookieService(): Promise<CookieService> {
        if (!ServiceFactory.cookieService) {
            ServiceFactory.cookieService = new CookieServiceImpl(new CookieRepository(await Database.getCollection("cookies")));
        }
        return ServiceFactory.cookieService;
    }

    public static async getSessionService(): Promise<SessionService> {
        if (!ServiceFactory.sessionService) {
            ServiceFactory.sessionService = new SessionServiceImpl(new SessionRepository(await Database.getCollection("sessions")));
        }
        return ServiceFactory.sessionService;
    }

    public static async init() {
        console.log(ServiceFactory.getUserService());
    }


}