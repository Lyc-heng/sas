#include <windows.h>
#include <stdio.h>
#include <tlhelp32.h>

int main() {
	char szDllName[] = "C:\\test\\HookFindFileW.dll";
	char szExeName[] = "hacker.exe";

	// ��ȡ�����б����Ŀ����̵�PID
	PROCESSENTRY32 ProcessEntry = {};
	ProcessEntry.dwSize = sizeof(PROCESSENTRY32);
	HANDLE hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
	bool bRet = Process32First(hProcessSnap, &ProcessEntry);
	DWORD dwProcessId = 0;
	while (bRet) {
		if (strcmp(szExeName, ProcessEntry.szExeFile) == 0) {
			dwProcessId = ProcessEntry.th32ProcessID;
			printf(ProcessEntry.szExeFile);
			break;
		}
		bRet = Process32Next(hProcessSnap, &ProcessEntry);
	}
	if (0 == dwProcessId) {
		printf("�Ҳ�������\n");
		return 1;
	}

	// ����PID��ý��̾��
	HANDLE hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, dwProcessId);
	if (0 == hProcess) {
		printf("�޷��򿪽���\n");
		return 1;
	}

	// �ڽ��̵���ȥ����ռ�
	size_t length = strlen(szDllName) + 1;
	char * pszDllFile = (char *)VirtualAllocEx(hProcess, NULL, length, MEM_COMMIT, PAGE_READWRITE);
	if (0 == pszDllFile) {
		printf("Զ�̿ռ����ʧ��\n");
		return 1;
	}

	// �������Ĳ���д�����̿ռ���ȥ
	if (!WriteProcessMemory(hProcess, (PVOID)pszDllFile, (PVOID)szDllName, length, NULL)) {
		printf("Զ�̿ռ�д��ʧ��\n");
		return 1;
	}

	// ��ȡLoadLibraryA����
	PTHREAD_START_ROUTINE pfnThreadRtn = (PTHREAD_START_ROUTINE)GetProcAddress(GetModuleHandle("kernel32"), "LoadLibraryA");
	if (0 == pfnThreadRtn) {
		printf("LoadLibraryA������ַ��ȡʧ��\n");
		return 1;
	}

	// ��Ŀ������и��ݺ�����ַ�Ͳ�����������
	HANDLE hThread = CreateRemoteThread(hProcess, NULL, 0, pfnThreadRtn, (PVOID)pszDllFile, 0, NULL);
	if (0 == hThread) {
		printf("Զ���̴߳���ʧ��\n");
		return 1;
	}

	// �ȴ�����ִ�����
	WaitForSingleObject(hThread, INFINITE);
	printf("Զ���߳�ִ�����!\n");

	VirtualFreeEx(hProcess, (PVOID)pszDllFile, 0, MEM_RELEASE);
	CloseHandle(hThread);
	CloseHandle(hProcess);

	system("pause");

	return 0;
}