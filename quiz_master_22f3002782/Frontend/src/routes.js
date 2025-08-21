import { createWebHistory, createRouter } from 'vue-router';
import HomePage from './components/HomePage.vue';
import LoginPage from './components/LoginPage.vue';
import RegisterPage from './components/RegisterPage.vue';
import DashboardPage from './components/DashboardPage.vue';
import SubjectsPage from './components/SubjectsPage.vue';
import ChaptersPage from './components/ChaptersPage.vue';
import QuizzesPage from './components/QuizzesPage.vue';
import TakeQuizPage from './components/TakeQuizPage.vue';
import QuizResultsPage from './components/QuizResultsPage.vue';
import ProfilePage from './components/ProfilePage.vue';
import ScoresPage from './components/ScoresPage.vue';
import AdminPage from './components/AdminPage.vue';
import AdminUsersPage from './components/AdminUsersPage.vue';
import AdminSubjectsPage from './components/AdminSubjectsPage.vue';
import AdminChaptersPage from './components/AdminChaptersPage.vue';
import AdminQuizzesPage from './components/AdminQuizzesPage.vue';
import AdminQuestionsPage from './components/AdminQuestionsPage.vue';
import AdminAnalyticsPage from './components/AdminAnalyticsPage.vue';
import UserPage from './components/UserPage.vue';
import NotFoundPage from './components/NotFoundPage.vue';

const routes = [
    { 
        path: '/', 
        name: 'Home',
        component: HomePage 
    },
    { 
        path: '/login', 
        name: 'Login',
        component: LoginPage 
    },
    { 
        path: '/register', 
        name: 'Register',
        component: RegisterPage 
    },
    { 
        path: '/dashboard', 
        name: 'Dashboard',
        component: DashboardPage,
        meta: { requiresAuth: true }
    },
    { 
        path: '/subjects', 
        name: 'Subjects',
        component: SubjectsPage 
    },
    { 
        path: '/subjects/:subjectId/chapters', 
        name: 'Chapters',
        component: ChaptersPage,
        meta: { requiresAuth: true }
    },
    { 
        path: '/chapters/:chapterId/quizzes', 
        name: 'Quizzes',
        component: QuizzesPage,
        meta: { requiresAuth: true }
    },
    { 
        path: '/take-quiz/:quizId', 
        name: 'TakeQuiz',
        component: TakeQuizPage,
        meta: { requiresAuth: true }
    },
    { 
        path: '/quiz-results/:scoreId', 
        name: 'QuizResults',
        component: QuizResultsPage,
        meta: { requiresAuth: true }
    },
    { 
        path: '/profile', 
        name: 'Profile',
        component: ProfilePage,
        meta: { requiresAuth: true }
    },
    { 
        path: '/scores', 
        name: 'Scores',
        component: ScoresPage,
        meta: { requiresAuth: true }
    },
    { 
        path: '/users', 
        name: 'Users',
        component: UserPage 
    },
    // Admin routes (protected)
    { 
        path: '/admin', 
        name: 'Admin',
        component: AdminPage,
        meta: { requiresAuth: true, requiresAdmin: true }
    },
    { 
        path: '/admin/users', 
        name: 'AdminUsers',
        component: AdminUsersPage,
        meta: { requiresAuth: true, requiresAdmin: true }
    },
    { 
        path: '/admin/subjects', 
        name: 'AdminSubjects',
        component: AdminSubjectsPage,
        meta: { requiresAuth: true, requiresAdmin: true }
    },
    { 
        path: '/admin/chapters', 
        name: 'AdminChapters',
        component: AdminChaptersPage,
        meta: { requiresAuth: true, requiresAdmin: true }
    },
    { 
        path: '/admin/quizzes', 
        name: 'AdminQuizzes',
        component: AdminQuizzesPage,
        meta: { requiresAuth: true, requiresAdmin: true }
    },
    { 
        path: '/admin/questions', 
        name: 'AdminQuestions',
        component: AdminQuestionsPage,
        meta: { requiresAuth: true, requiresAdmin: true }
    },
    { 
        path: '/admin/analytics', 
        name: 'AdminAnalytics',
        component: AdminAnalyticsPage,
        meta: { requiresAuth: true, requiresAdmin: true }
    },
    // 404 page
    { 
        path: '/:pathMatch(.*)*', 
        name: 'NotFound',
        component: NotFoundPage 
    }
]

export const router = createRouter({
    history: createWebHistory(),
    routes
});

// Route guards
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token');
    const userData = localStorage.getItem('userData');
    
    // Check if route requires authentication
    if (to.meta.requiresAuth && !token) {
        // Redirect to login if not authenticated
        next('/login');
        return;
    }
    
    // Check if route requires admin access
    if (to.meta.requiresAdmin && token && userData) {
        const user = JSON.parse(userData);
        const isAdmin = user.roles && user.roles.includes('admin');
        
        if (!isAdmin) {
            // Redirect to dashboard if not admin
            next('/dashboard');
            return;
        }
    }
    
    // If user is logged in and tries to access login/register, redirect appropriately
    if ((to.path === '/login' || to.path === '/register') && token && userData) {
        const user = JSON.parse(userData);
        const isAdmin = user.roles && user.roles.includes('admin');
        
        if (isAdmin) {
            next('/admin');
        } else {
            next('/dashboard');
        }
        return;
    }
    
    next();
});